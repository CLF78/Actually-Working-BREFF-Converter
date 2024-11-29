#!/usr/bin/env python3

# params.py
# Emitter parameter definitions

from common.field import *
from emitter.flags import EmitterShape

class DiscParams(Structure):
    x_size = f32()
    inner_radius = f32()
    angle_start = f32()
    angle_end = f32()
    z_size = f32('f4x')


class LineParams(Structure):
    length = f32()
    x_rot = f32()
    y_rot = f32()
    z_rot = f32('f8x')


class CubeParams(Structure):
    x_size = f32()
    y_size = f32()
    z_size = f32()
    inner_radius = f32('f8x')


class CylindereSphereTorusParams(Structure):
    x_size = f32()
    inner_radius = f32()
    angle_start = f32()
    angle_end = f32()
    y_size = f32()
    z_size = f32()


def get_emitter_params(emitter: Structure) -> Field:
    shape = emitter.emitter_flags.shape
    if shape == EmitterShape.Point:
        return padding(24)
    elif shape == EmitterShape.Disc:
        return StructField(DiscParams)
    elif shape == EmitterShape.Line:
        return StructField(LineParams)
    elif shape == EmitterShape.Cube:
        return StructField(CubeParams)
    else:
        return StructField(CylindereSphereTorusParams)
