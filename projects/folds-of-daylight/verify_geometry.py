"""독립 기하 검사. 기본 실행은 읽기 전용이며 --report일 때만 보고서를 쓴다.

    python verify_geometry.py
    python verify_geometry.py --report

build.py를 import/exec하지 않는다. 허용한 수식/반복문만 AST로 읽어
내보낸 geometry.json과 비교한 뒤, 표면의 실제 좌표와 연결 구조를 검사한다.
Blender 실행, 렌더, 원본 변경, 물리/제조 가능성 검사는 하지 않는다.
"""

import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
import math
import operator
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DISTANCE_TOLERANCE = 1e-9
AREA_TOLERANCE = 1e-9


def numeric_expression(node, names):
    """허용한 수식만 해석한다. eval/exec나 임의 Python 함수는 호출하지 않는다."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        return [numeric_expression(item, names) for item in node.elts]
    binary = {ast.Add: operator.add, ast.Sub: operator.sub,
              ast.Mult: operator.mul, ast.Div: operator.truediv,
              ast.Mod: operator.mod}
    if isinstance(node, ast.BinOp) and type(node.op) in binary:
        return binary[type(node.op)](numeric_expression(node.left, names),
                                     numeric_expression(node.right, names))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = numeric_expression(node.operand, names)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.IfExp):
        branch = node.body if numeric_expression(node.test, names) else node.orelse
        return numeric_expression(branch, names)
    if isinstance(node, ast.Call) and not node.keywords:
        args = [numeric_expression(arg, names) for arg in node.args]
        if isinstance(node.func, ast.Name) and node.func.id == 'range':
            values = range(*args)
            if len(values) > 10000:
                raise ValueError('소스의 반복 범위가 검사 한도를 초과합니다.')
            return values
        if (isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == 'math'
                and node.func.attr in ('sin', 'cos', 'radians')):
            return getattr(math, node.func.attr)(*args)
    if isinstance(node, ast.ListComp) and len(node.generators) == 1:
        generator = node.generators[0]
        if (isinstance(generator.target, ast.Name) and not generator.ifs
                and not generator.is_async):
            return [numeric_expression(node.elt, {**names, generator.target.id: value})
                    for value in numeric_expression(generator.iter, names)]
    raise ValueError('지원하지 않는 소스 표현식: ' + ast.dump(node))


def source_geometry(path):
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=path.name)
    names = {}
    wanted = {'N', 'start', 'sweep', 'inner', 'outer', 'slope'}
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
            if isinstance(target, ast.Name) and target.id in wanted:
                names[target.id] = numeric_expression(statement.value, names)
    if set(names) != wanted:
        raise ValueError('필수 기하 매개변수 6개를 찾지 못했습니다.')
    vertices = []

    def inspect_statements(statements, scope):
        for statement in statements:
            if isinstance(statement, ast.For) and isinstance(statement.target, ast.Name):
                if statement.orelse:
                    raise ValueError('예상하지 않은 반복문 else 절입니다.')
                for value in numeric_expression(statement.iter, scope):
                    scope[statement.target.id] = value
                    inspect_statements(statement.body, scope)
            elif (isinstance(statement, ast.Assign) and len(statement.targets) == 1
                  and isinstance(statement.targets[0], ast.Name)):
                scope[statement.targets[0].id] = numeric_expression(statement.value, scope)
            elif (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
                  and isinstance(statement.value.func, ast.Attribute)
                  and isinstance(statement.value.func.value, ast.Name)
                  and statement.value.func.value.id == 'verts'
                  and statement.value.func.attr == 'append'
                  and len(statement.value.args) == 1 and not statement.value.keywords):
                vertices.append(numeric_expression(statement.value.args[0], scope))
            else:
                raise ValueError('꼭짓점 생성 반복문에 지원하지 않는 문장이 있습니다.')

    loops = [statement for statement in tree.body if isinstance(statement, ast.For)
             and any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                     and isinstance(node.func.value, ast.Name)
                     and node.func.value.id == 'verts' and node.func.attr == 'append'
                     for node in ast.walk(statement))]
    if len(loops) != 1:
        raise ValueError('최상위 꼭짓점 생성 반복문은 정확히 하나여야 합니다.')
    inspect_statements(loops, dict(names))
    faces = None
    for statement in tree.body:
        if (isinstance(statement, ast.Assign) and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name)
                and statement.targets[0].id == 'faces'):
            faces = numeric_expression(statement.value, names)
    if faces is None:
        raise ValueError('소스에서 면 목록을 찾지 못했습니다.')
    return vertices, faces, names


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def length(vector):
    return math.sqrt(dot(vector, vector))


def components(nodes, adjacency):
    remaining = set(nodes)
    count = 0
    while remaining:
        count += 1
        stack = [remaining.pop()]
        while stack:
            for neighbor in adjacency.get(stack.pop(), ()):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    return count


def inspect_geometry(vertices, faces, expected_vertices, expected_faces, parameters):
    checks = {}

    def check(name, passed, measured, expected):
        checks[name] = {'status': 'pass' if passed else 'fail',
                        'measured': measured, 'expected': expected}

    valid_vertices = (bool(vertices) and all(isinstance(v, (list, tuple)) and len(v) == 3
                      and all(type(x) in (int, float) and math.isfinite(x) for x in v)
                      for v in vertices))
    valid_faces = (bool(faces) and all(isinstance(f, (list, tuple)) and len(f) == 4
                   and len(set(f)) == 4 and all(type(i) is int and 0 <= i < len(vertices)
                                               for i in f) for f in faces))
    check('valid_vertices_and_quad_indices', valid_vertices and valid_faces,
          {'vertices_valid': valid_vertices, 'faces_valid': valid_faces}, True)
    if not valid_vertices or not valid_faces:
        return {'checks': checks, 'panels': [], 'status': 'fail'}

    coordinate_error = (max(length(subtract(a, b)) for a, b in zip(vertices, expected_vertices))
                        if len(vertices) == len(expected_vertices) else None)
    check('export_matches_source', coordinate_error is not None
          and coordinate_error <= DISTANCE_TOLERANCE and faces == expected_faces,
          {'maximum_coordinate_error': coordinate_error,
           'face_indices_match': faces == expected_faces},
          '연결 구조가 같고 좌표 차이가 거리 허용 오차 이내여야 함.')
    check('panel_count', len(faces) == parameters['N'] == 24, len(faces), 24)
    check('vertex_count', len(vertices) == 50, len(vertices), 50)

    edge_uses = defaultdict(list)
    vertex_adjacency = defaultdict(set)
    face_adjacency = defaultdict(set)
    panels = []
    for index, face in enumerate(faces):
        polygon = [vertices[i] for i in face]
        normal_vector = cross(subtract(polygon[1], polygon[0]),
                              subtract(polygon[2], polygon[0]))
        normal_length = length(normal_vector)
        normal = tuple(value / normal_length for value in normal_vector) if normal_length else (0, 0, 0)
        deviation = max(abs(dot(subtract(p, polygon[0]), normal)) for p in polygon)
        area = sum(length(cross(subtract(polygon[i], polygon[0]),
                                subtract(polygon[i + 1], polygon[0]))) / 2
                   for i in range(1, len(polygon) - 1))
        turns = [dot(cross(subtract(polygon[(j + 1) % 4], polygon[j]),
                           subtract(polygon[(j + 2) % 4], polygon[(j + 1) % 4])), normal)
                 for j in range(4)]
        panels.append({'panel': index + 1, 'area': area,
                       'max_plane_distance': deviation, 'unit_normal': list(normal),
                       'strictly_convex': min(turns) > AREA_TOLERANCE})
        for j, a in enumerate(face):
            b = face[(j + 1) % len(face)]
            edge_uses[tuple(sorted((a, b)))].append((index, a, b))
            vertex_adjacency[a].add(b)
            vertex_adjacency[b].add(a)
    for uses in edge_uses.values():
        for face_id, _, _ in uses:
            face_adjacency[face_id].update(other for other, _, _ in uses if other != face_id)
    boundary = [edge for edge, uses in edge_uses.items() if len(uses) == 1]
    boundary_adjacency = defaultdict(set)
    for a, b in boundary:
        boundary_adjacency[a].add(b)
        boundary_adjacency[b].add(a)
    boundary_loops = (components(boundary_adjacency, boundary_adjacency)
                      if all(len(neighbors) == 2 for neighbors in boundary_adjacency.values())
                      else None)
    face_components = components(range(len(faces)), face_adjacency)
    vertex_components = components(range(len(vertices)), vertex_adjacency)
    edge_counts = Counter(len(uses) for uses in edge_uses.values())
    conflicting = sum(len(uses) == 2 and uses[0][1:] != uses[1][1:][::-1]
                      for uses in edge_uses.values())
    euler = len(vertices) - len(edge_uses) + len(faces)
    check('connected_sheet', face_components == 1 and vertex_components == 1,
          {'face_components': face_components, 'vertex_components': vertex_components},
          '면과 꼭짓점이 각각 하나로 연결되고 사용하지 않는 꼭짓점이 없어야 함.')
    check('open_strip_topology', len(edge_uses) == 73 and edge_counts == {1: 50, 2: 23}
          and boundary_loops == 1 and euler == 1,
          {'edges': len(edge_uses), 'boundary_edges': edge_counts[1],
           'interior_edges': edge_counts[2], 'nonmanifold_edges': sum(v for k, v in edge_counts.items() if k > 2),
           'boundary_loops': boundary_loops, 'euler_characteristic': euler},
          {'edges': 73, 'boundary_edges': 50, 'interior_edges': 23,
           'boundary_loops': 1, 'euler_characteristic': 1})
    check('consistent_shared_edge_winding', conflicting == 0, conflicting, 0)
    max_deviation = max(panel['max_plane_distance'] for panel in panels)
    check('panel_planarity', max_deviation <= DISTANCE_TOLERANCE,
          max_deviation, {'maximum': DISTANCE_TOLERANCE})
    areas = [panel['area'] for panel in panels]
    theoretical_area = ((parameters['outer'] ** 2 - parameters['inner'] ** 2) / 2
                        * math.sqrt(math.sin(parameters['sweep'] / parameters['N']) ** 2
                                    + parameters['slope'] ** 2))
    check('nonzero_panel_areas', min(areas) > AREA_TOLERANCE,
          {'minimum': min(areas), 'maximum': max(areas), 'total': sum(areas)},
          {'minimum_greater_than': AREA_TOLERANCE})
    check('area_matches_independent_formula',
          max(abs(area - theoretical_area) for area in areas) <= AREA_TOLERANCE,
          {'expected_each': theoretical_area,
           'maximum_error': max(abs(area - theoretical_area) for area in areas)},
          {'maximum_error': AREA_TOLERANCE})
    check('convex_panels', all(panel['strictly_convex'] for panel in panels),
          sum(panel['strictly_convex'] for panel in panels), len(panels))
    minimum_normal_z = min(panel['unit_normal'][2] for panel in panels)
    check('upward_panel_normals', minimum_normal_z > DISTANCE_TOLERANCE,
          {'minimum_normal_z': minimum_normal_z}, '모든 법선의 z 성분이 양수여야 함.')
    minimum_z = min(v[2] for v in vertices)
    check('base_surface_above_ground', minimum_z >= -DISTANCE_TOLERANCE,
          {'minimum_z': minimum_z, 'maximum_z': max(v[2] for v in vertices)},
          '모든 꼭짓점과 볼록 평면 패널 내부가 z = 0 이상이어야 함.')
    return {'status': 'pass' if all(c['status'] == 'pass' for c in checks.values()) else 'fail',
            'checks': checks, 'panels': panels}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'build.py')
    parser.add_argument('--geometry', type=Path, default=ROOT / 'output' / 'geometry.json')
    parser.add_argument('--report', action='store_true', help='geometry_qa.json 기록. 생략하면 화면 출력만 수행.')
    args = parser.parse_args(argv)
    source_vertices, source_faces, parameters = source_geometry(args.source)
    exported = json.loads(args.geometry.read_text(encoding='utf-8'))
    report = inspect_geometry(exported['vertices'], exported['faces'],
                              source_vertices, source_faces, parameters)
    report.update({
        'schema_version': 1,
        'scope': '기본 24개 평면 패널의 좌표·위상 검사. Blender modifier 결과 검사는 미실행.',
        'units': '장면 단위 및 장면 단위의 제곱. 실물 단위로 환산하지 않음.',
        'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
        'geometry_sha256': hashlib.sha256(args.geometry.read_bytes()).hexdigest(),
        'parameters': parameters,
        'tolerances': {'distance': DISTANCE_TOLERANCE, 'area': AREA_TOLERANCE},
        'unrun_checks': [
            {'check': 'solidify_bevel_mesh_closed_manifold', 'status': 'not_run'},
            {'check': 'solidify_bevel_mesh_positive_signed_volume', 'status': 'not_run'},
            {'check': 'solidify_bevel_mesh_ground_penetration', 'status': 'not_run'},
        ],
        'unrun_reason': 'Blender 실행이 종료 코드 137로 중단되어 .blend 및 modifier 적용 메시가 생성되지 않음. 이 검증기는 Blender를 실행하지 않음.',
        'limitations': [
            'status는 실행한 기본 표면 검사만의 결과이며 최종 Blender 메시의 통과를 뜻하지 않음.',
            '기본 표면은 경계가 있는 두께 없는 메시이다. 닫힌 입체나 양의 부피라고 주장하지 않음.',
            '전역 자기 교차, 그림자의 광학적 정확성, SVG 가림 순서 및 렌더 품질은 이 검사 범위가 아님.',
            '종이 물성, 접힘 과정, 응력, 안정성, 실물 제작 가능성 및 물리 시뮬레이션은 검증하지 않음.',
        ],
    })
    serialized = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.report:
        (ROOT / 'geometry_qa.json').write_text(serialized, encoding='utf-8')
    print(serialized, end='')
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
