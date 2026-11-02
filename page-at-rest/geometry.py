"""Shared original sculpture geometry; coordinates are millimetres.

This is an artistic interpretation, not a dimension recovery from the reference.
The Blender page edge and FreeCAD cradle use this SAME function.
"""
import math


def page_point(page, paper, u, v):
    width = page['width_bottom'] * (1-v) + page['width_top'] * v
    # A single broad opening, with a small returning curl at the upper corners.
    x = page['side'] * (paper['half_gap'] + width*u + 8*math.sin(math.pi*v) + 10*v*v)
    y = -7 + 25*u + 8*math.sin(math.pi*u) + 22*math.sin(math.pi*v)*(1-.3*u) + 20*(v**4)*(u**4)
    upper = math.sin(u*math.pi*.5)
    z = paper['root_z'] + page['height']*v + page['outer_lift_bottom']*u*(1-v) + page['outer_lift_top']*upper*v
    z += 2.0*math.sin(math.pi*u)*math.sin(math.pi*v)
    return (x, y, z)


def cradle_point(page, params, u):
    p = page_point(page, params['paper'], u, 0)
    # A shallow intentional seat at the lower edge, not an unsupported gap.
    return (p[0], p[1], p[2]-params['supports']['radius']+params['supports']['seat_insertion'])
