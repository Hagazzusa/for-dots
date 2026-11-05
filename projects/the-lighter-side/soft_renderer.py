"""Small deterministic, two-sided orthographic triangle renderer.

World Z is up. ``camera`` is the eye position, looking toward ``target``;
``ortho_scale`` is the FULL vertical world-space span (horizontal span follows
width / height). Pixel Y points down. Depth is distance along the viewing
axis; smaller positive depth wins. Fragments behind the eye are discarded.
A near-vertical view uses world Y as its up reference. Mesh winding does not
cause culling: normals are flipped toward the eye before Lambert shading.

Requires only NumPy and Pillow. Degenerate triangles are skipped. Invalid
sizes, nonfinite coordinates/colors, non-triangular faces, invalid indices,
and a camera coincident with its target raise ValueError. No perspective,
shadows, transparency, textures, or color management are applied. Coplanar
ties preserve the first submitted face. Input meshes are never modified.
"""

import operator

import numpy as np
from PIL import Image


def _positive_int(value, name):
    try:
        result = operator.index(value)
    except TypeError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if isinstance(value, (bool, np.bool_)) or result < 1:
        raise ValueError(f"{name} must be a positive integer")
    return result


def _vector(value, name):
    result = np.asarray(value, dtype=np.float64)
    if result.shape != (3,) or not np.isfinite(result).all():
        raise ValueError(f"{name} must contain three finite numbers")
    return result


def render_meshes(meshes, width, height, camera, target, ortho_scale,
                  background=(244, 241, 232), supersample=2):
    """Return a Pillow RGB image; mesh colors are RGB floats in [0, 1].

    ``meshes`` is an iterable of dictionaries with ``vertices`` (N x 3),
    ``faces`` (M x 3 integer indices), and ``color`` (three floats). Empty
    vertex/face lists are supported. Supersampling uses Lanczos downsampling.
    Light is fixed above and to camera-left, with 76% ambient illumination.
    """
    width = _positive_int(width, "width")
    height = _positive_int(height, "height")
    supersample = _positive_int(supersample, "supersample")
    eye = _vector(camera, "camera")
    target = _vector(target, "target")
    bg = _vector(background, "background")
    if np.any((bg < 0) | (bg > 255)):
        raise ValueError("background must be RGB values in [0, 255]")
    if not np.isscalar(ortho_scale) or not np.isfinite(ortho_scale) or ortho_scale <= 0:
        raise ValueError("ortho_scale must be finite and positive")
    forward = target - eye
    norm = np.linalg.norm(forward)
    if norm < 1e-12:
        raise ValueError("camera and target must differ")
    forward /= norm
    world_up = np.array([0., 0., 1.])
    if abs(np.dot(forward, world_up)) > .999:
        world_up = np.array([0., 1., 0.])
    right = np.cross(forward, world_up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    light = -.4 * right + .65 * up - .75 * forward
    light /= np.linalg.norm(light)
    w, h = width * supersample, height * supersample
    pixels_per_unit = h / float(ortho_scale)
    pixels = np.empty((h, w, 3), dtype=np.uint8)
    pixels[:] = np.rint(bg).astype(np.uint8)
    zbuffer = np.full((h, w), np.inf, dtype=np.float64)

    for mesh_index, mesh in enumerate(meshes):
        vertices = np.asarray(mesh["vertices"], dtype=np.float64)
        faces = np.asarray(mesh["faces"])
        color = _vector(mesh["color"], f"mesh {mesh_index} color")
        if np.any((color < 0) | (color > 1)):
            raise ValueError("mesh colors must lie in [0, 1]")
        if vertices.size == 0:
            vertices = vertices.reshape((0, 3))
        if vertices.ndim != 2 or vertices.shape[1] != 3 or not np.isfinite(vertices).all():
            raise ValueError("vertices must be a finite N x 3 array")
        if faces.size == 0:
            continue
        if faces.ndim != 2 or faces.shape[1] != 3 or not np.issubdtype(faces.dtype, np.integer):
            raise ValueError("faces must be an M x 3 integer array")
        if faces.min() < 0 or faces.max() >= len(vertices):
            raise ValueError("face index out of range")
        relative = vertices - eye
        projected = np.column_stack((w * .5 + relative @ right * pixels_per_unit,
                                     h * .5 - relative @ up * pixels_per_unit,
                                     relative @ forward))
        for face in faces:
            tri = projected[face]
            if np.max(tri[:, 2]) <= 0:
                continue
            xmin = max(0, int(np.ceil(tri[:, 0].min() - .5)))
            xmax = min(w - 1, int(np.floor(tri[:, 0].max() - .5)))
            ymin = max(0, int(np.ceil(tri[:, 1].min() - .5)))
            ymax = min(h - 1, int(np.floor(tri[:, 1].max() - .5)))
            if xmin > xmax or ymin > ymax:
                continue
            a, b, c = tri
            denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(denominator) < 1e-12:
                continue
            xs = np.arange(xmin, xmax + 1)[None, :] + .5
            ys = np.arange(ymin, ymax + 1)[:, None] + .5
            wa = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / denominator
            wb = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / denominator
            wc = 1. - wa - wb
            depth = wa * a[2] + wb * b[2] + wc * c[2]
            region_z = zbuffer[ymin:ymax + 1, xmin:xmax + 1]
            visible = ((wa >= -1e-10) & (wb >= -1e-10) & (wc >= -1e-10)
                       & (depth > 0) & (depth < region_z))
            if not np.any(visible):
                continue
            va, vb, vc = vertices[face]
            normal = np.cross(vb - va, vc - va)
            normal_length = np.linalg.norm(normal)
            if normal_length < 1e-15:
                continue
            normal /= normal_length
            if np.dot(normal, forward) > 0:
                normal = -normal
            shade = .76 + .24 * max(0., np.dot(normal, light))
            shaded_color = np.rint(color * shade * 255).astype(np.uint8)
            region_z[visible] = depth[visible]
            pixels[ymin:ymax + 1, xmin:xmax + 1][visible] = shaded_color
    result = Image.fromarray(pixels)
    if supersample > 1:
        result = result.resize((width, height), Image.Resampling.LANCZOS)
    return result
