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
    match emitter.emitter_flags.shape:
        case EmitterShape.Point:
            return padding(24)
        case EmitterShape.Disc:
            return StructField(DiscParams)
        case EmitterShape.Line:
            return StructField(LineParams)
        case EmitterShape.Cube:
            return StructField(CubeParams)
        case _:
            return StructField(CylindereSphereTorusParams)
