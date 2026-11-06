"""작은 표본으로 굴절 구현을 독립 점검한다. --report가 없으면 파일을 쓰지 않는다."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

# 읽기 전용 실행에서 의존 모듈의 바이트코드 캐시도 만들지 않는다.
sys.dont_write_bytecode = True
import numpy as np


ROOT = Path(__file__).resolve().parent


def load_builder():
    """검사만 실행할 때 __pycache__도 남기지 않는다."""
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("floor_builder", ROOT / "build.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous


def scalar_height(x, y, time, model):
    """제작 함수와 분리한 스칼라 높이식. 기울기는 여기서 계산하지 않는다."""
    return math.fsum(
        wave["amplitude"]
        * math.cos(
            math.tau
            * (
                (wave["nx"] * x + wave["ny"] * y) / model["domain_size"]
                + wave["cycles"] * time / model["loop_seconds"]
            )
            + wave["phase"]
        )
        for wave in model["waves"]
    )


def numerical_slopes(x, y, time, model, step=1e-5):
    """중앙 유한차분으로 수면 법선을 독립적으로 구한다."""
    hx = (scalar_height(x + step, y, time, model) - scalar_height(x - step, y, time, model)) / (2 * step)
    hy = (scalar_height(x, y + step, time, model) - scalar_height(x, y - step, time, model)) / (2 * step)
    return hx, hy


def angle_ray(x, y, time, model):
    """벡터 굴절 공식을 재사용하지 않고 스넬각과 접선 성분으로 광선을 만든다."""
    h = scalar_height(x, y, time, model)
    hx, hy = numerical_slopes(x, y, time, model)
    normal = np.array([-hx, -hy, 1.0], dtype=float)
    normal /= np.linalg.norm(normal)
    incident = np.array([0.0, 0.0, -1.0])
    cosine_i = float(normal[2])
    tangent = incident + cosine_i * normal
    sine_i = float(np.linalg.norm(tangent))
    theta_t = math.asin(model["air_index"] / model["water_index"] * sine_i)
    ray = -math.cos(theta_t) * normal
    if sine_i > 1e-15:
        ray += math.sin(theta_t) * tangent / sine_i
    distance = (-model["bottom_depth"] - h) / ray[2]
    return np.array([x, y, h]) + distance * ray, ray


def periodic_blur(counts, sigma):
    """SciPy 호출 없이 작은 주기 격자에 분리형 가우스 합을 적용한다."""
    if sigma == 0:
        return counts.copy()
    radius = int(4.0 * sigma + 0.5)
    offsets = np.arange(-radius, radius + 1)
    kernel = np.exp(-(offsets * offsets) / (2 * sigma * sigma))
    kernel /= kernel.sum()
    result = counts.astype(float)
    for axis in (0, 1):
        result = sum(weight * np.roll(result, int(offset), axis=axis) for offset, weight in zip(offsets, kernel))
    return result


def verify():
    builder = load_builder()
    model = json.loads((ROOT / "model.json").read_text(encoding="utf-8"))
    checks = []

    def record(name, passed, metrics):
        checks.append({"name": name, "passed": bool(passed), "metrics": metrics})

    def maximum(value):
        return float(np.max(np.abs(value)))

    length = model["domain_size"]
    period = model["loop_seconds"]
    height_bound = sum(abs(wave["amplitude"]) for wave in model["waves"])
    integer_modes = all(
        float(wave[key]).is_integer()
        for wave in model["waves"]
        for key in ("nx", "ny", "cycles")
    )
    record(
        "모델 전제와 바닥 여유",
        length > 0 and period == 10.0 and model["bottom_depth"] > height_bound
        and 0 < model["air_index"] < model["water_index"] and integer_modes,
        {"domain_size": length, "bottom_depth": model["bottom_depth"],
         "air_index": model["air_index"], "water_index": model["water_index"],
         "wave_count": len(model["waves"]), "blur_sigma_pixels": model["blur_sigma_pixels"],
         "period_seconds": period, "integer_modes": integer_modes,
         "absolute_height_upper_bound": height_bound,
         "minimum_surface_floor_gap_bound": model["bottom_depth"] - height_bound},
    )

    rng = np.random.default_rng(20261106)
    x = rng.uniform(0, length, 257)
    y = rng.uniform(0, length, 257)
    times = [0.0, 0.137, 2.375, 5.0, 9.999]
    errors = {key: 0.0 for key in (
        "height", "finite_difference_slope", "normal_unit", "ray_unit", "snell_sines",
        "tangent_snell", "plane_residual", "reference_direction", "reference_endpoint",
        "loop_surface", "loop_direction", "loop_endpoint", "loop_endpoint_velocity",
        "spatial_surface", "spatial_direction", "spatial_endpoint",
    )}
    extrema = {"maximum_ray_z": -math.inf, "minimum_distance": math.inf, "minimum_transmitted_cosine": math.inf}
    all_finite = True
    for time in times:
        h, hx, hy = builder.surface(x, y, time, model)
        ex, ey, tx, ty, tz = builder.endpoints(x, y, time, model)
        rays = np.column_stack((tx, ty, tz))
        normals = np.column_stack((-hx, -hy, np.ones_like(h)))
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        heights = np.array([scalar_height(float(xx), float(yy), time, model) for xx, yy in zip(x, y)])
        slopes = np.array([numerical_slopes(float(xx), float(yy), time, model) for xx, yy in zip(x, y)])
        independent = [angle_ray(float(xx), float(yy), time, model) for xx, yy in zip(x, y)]
        reference_endpoints = np.array([item[0] for item in independent])
        reference_rays = np.array([item[1] for item in independent])
        incident = np.tile([0.0, 0.0, -1.0], (len(x), 1))
        sine_i = np.linalg.norm(np.cross(incident, normals), axis=1)
        sine_t = np.linalg.norm(np.cross(rays, normals), axis=1)
        dot_t = np.sum(rays * normals, axis=1)
        tangential_i = incident + normals[:, 2, None] * normals
        tangential_t = rays - dot_t[:, None] * normals
        distance = (-model["bottom_depth"] - h) / tz
        values = {
            "height": h - heights,
            "finite_difference_slope": np.column_stack((hx, hy)) - slopes,
            "normal_unit": np.linalg.norm(normals, axis=1) - 1,
            "ray_unit": np.linalg.norm(rays, axis=1) - 1,
            "snell_sines": model["air_index"] * sine_i - model["water_index"] * sine_t,
            "tangent_snell": model["air_index"] * tangential_i - model["water_index"] * tangential_t,
            "plane_residual": h + distance * tz + model["bottom_depth"],
            "reference_direction": rays - reference_rays,
            "reference_endpoint": np.column_stack((ex, ey)) - reference_endpoints[:, :2],
        }
        all_finite &= all(np.all(np.isfinite(value)) for value in (h, hx, hy, ex, ey, rays, distance))
        extrema["maximum_ray_z"] = max(extrema["maximum_ray_z"], float(tz.max()))
        extrema["minimum_distance"] = min(extrema["minimum_distance"], float(distance.min()))
        extrema["minimum_transmitted_cosine"] = min(extrema["minimum_transmitted_cosine"], float((-dot_t).min()))

        later_surface = np.array(builder.surface(x, y, time + period, model))
        later = np.array(builder.endpoints(x, y, time + period, model))
        original = np.array((ex, ey, tx, ty, tz))
        values["loop_surface"] = later_surface - np.array((h, hx, hy))
        values["loop_direction"] = later[2:] - original[2:]
        values["loop_endpoint"] = later[:2] - original[:2]
        dt = 1e-4
        velocity = (
            np.array(builder.endpoints(x, y, time + dt, model))[:2]
            - np.array(builder.endpoints(x, y, time - dt, model))[:2]
        ) / (2 * dt)
        later_velocity = (
            np.array(builder.endpoints(x, y, time + period + dt, model))[:2]
            - np.array(builder.endpoints(x, y, time + period - dt, model))[:2]
        ) / (2 * dt)
        values["loop_endpoint_velocity"] = later_velocity - velocity
        for dx, dy in ((length, 0.0), (0.0, length)):
            shifted_surface = np.array(builder.surface(x + dx, y + dy, time, model))
            shifted = np.array(builder.endpoints(x + dx, y + dy, time, model))
            errors["spatial_surface"] = max(errors["spatial_surface"], maximum(shifted_surface - np.array((h, hx, hy))))
            errors["spatial_direction"] = max(errors["spatial_direction"], maximum(shifted[2:] - original[2:]))
            errors["spatial_endpoint"] = max(errors["spatial_endpoint"], maximum(shifted[:2] - original[:2] - np.array([[dx], [dy]])))
        for key, value in values.items():
            errors[key] = max(errors[key], maximum(value))

    record("높이와 유한차분 기울기", errors["height"] < 1e-12 and errors["finite_difference_slope"] < 2e-8,
           {key: errors[key] for key in ("height", "finite_difference_slope")})
    record("단위벡터와 아래쪽 전파", all_finite and errors["normal_unit"] < 1e-12 and errors["ray_unit"] < 1e-12
           and extrema["maximum_ray_z"] < 0 and extrema["minimum_transmitted_cosine"] > 0,
           {"all_finite": bool(all_finite), "normal_unit_error": errors["normal_unit"], "ray_unit_error": errors["ray_unit"], **extrema})
    record("스넬의 사인 관계와 접선 방향", errors["snell_sines"] < 1e-12 and errors["tangent_snell"] < 1e-12,
           {key: errors[key] for key in ("snell_sines", "tangent_snell")})
    record("독립 각도식과 바닥 교차", errors["reference_direction"] < 2e-8 and errors["reference_endpoint"] < 5e-8
           and errors["plane_residual"] < 1e-12 and extrema["minimum_distance"] > 0,
           {key: errors[key] for key in ("reference_direction", "reference_endpoint", "plane_residual")})
    record("10초 반복의 위치·방향·이동속도", all(errors[key] < tolerance for key, tolerance in (
        ("loop_surface", 1e-12), ("loop_direction", 1e-12), ("loop_endpoint", 1e-12), ("loop_endpoint_velocity", 1e-8))),
        {key: errors[key] for key in ("loop_surface", "loop_direction", "loop_endpoint", "loop_endpoint_velocity")})
    record("6×6 공간 주기", all(errors[key] < 1e-12 for key in ("spatial_surface", "spatial_direction", "spatial_endpoint")),
           {key: errors[key] for key in ("spatial_surface", "spatial_direction", "spatial_endpoint")})

    flat = copy.deepcopy(model)
    flat["waves"] = []
    flat_end = np.array(builder.endpoints(x, y, 3.75, flat))
    flat_expected = np.array((x, y, np.zeros_like(x), np.zeros_like(x), -np.ones_like(x)))
    flat_image, flat_total = builder.irradiance(3.75, flat, 64, 32)
    flat_error = maximum(flat_end - flat_expected)
    uniform_error = maximum(flat_image - 1.0)
    record("평탄 수면 대조", flat_error < 1e-12 and uniform_error < 1e-12 and flat_total == 64 ** 2,
           {"endpoint_direction_error": flat_error, "uniform_density_error": uniform_error, "ray_count": int(flat_total)})

    count_runs = []
    for rays, pixels in ((17, 16), (33, 31), (65, 64), (130, 37)):
        for time in (0.0, 2.375, 9.999):
            density, total = builder.irradiance(time, model, rays, pixels)
            count_runs.append({"rays_per_axis": rays, "pixels_per_axis": pixels, "time_seconds": time,
                               "raw_ray_count": int(total), "expected_ray_count": rays ** 2,
                               "normalized_mean_error": abs(float(density.mean()) - 1.0),
                               "finite_nonnegative": bool(np.all(np.isfinite(density)) and np.all(density >= 0))})
    record("광선 개수와 흐림 후 평균 보존", all(
        item["raw_ray_count"] == item["expected_ray_count"] and item["normalized_mean_error"] < 1e-12
        and item["finite_nonnegative"] for item in count_runs), {"runs": count_runs})

    rays, pixels, time = 65, 31, 0.63789
    counts = np.zeros((pixels, pixels), dtype=np.int64)
    wrapped = 0
    for row in range(rays):
        for column in range(rays):
            xx, yy = (column + 0.5) * length / rays, (row + 0.5) * length / rays
            hit, _ = angle_ray(xx, yy, time, model)
            wrapped += int(not (0 <= hit[0] < length and 0 <= hit[1] < length))
            ix, iy = int(math.floor((hit[0] % length) / length * pixels)), int(math.floor((hit[1] % length) / length * pixels))
            counts[iy, ix] += 1
    reference_density = periodic_blur(counts, model["blur_sigma_pixels"]) / (rays ** 2 / pixels ** 2)
    density, total = builder.irradiance(time, model, rays, pixels)
    density_error = maximum(density - reference_density)
    record("독립 픽셀 집계·주기 경계·가우스 흐림", int(counts.sum()) == rays ** 2 and total == rays ** 2
           and wrapped > 0 and density_error < 1e-10,
           {"rays_per_axis": rays, "pixels_per_axis": pixels, "time_seconds": time,
            "reference_ray_count": int(counts.sum()), "boundary_wrapped_rays": wrapped,
            "normalized_density_max_error": density_error})

    return {
        "schema_version": 1,
        "passed": all(check["passed"] for check in checks),
        "scope": "정해진 사인파 그래프 수면에 대한 기하광학 구현의 수치적 자기일관성 검사",
        "not_validated": ["실측 또는 유체역학적 정확성", "파동광학·간섭·회절", "색의 측정 정확성", "절대 방사조도·실제 투과 에너지", "완성 영상의 픽셀 단위 무이음성"],
        "sampling": {"seed": 20261106, "points_per_time": len(x), "times_seconds": times,
                     "finite_difference_step": 1e-5, "largest_ray_grid_per_axis": 130,
                     "largest_density_grid_per_axis": 64},
        "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ("model.json", "build.py", "verify_optics.py")},
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="이 옵션이 있을 때만 검사 결과 JSON을 지정한 경로에 쓴다.")
    args = parser.parse_args()
    report = verify()
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report is not None:
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
