#!/usr/bin/env python3

# lighting.py
# Emitter lighting definitions

from enum import auto
from common.common import CEnum
from common.field import *
from common.nw4r import VEC3
from common.gx import GXColor

class LightingMode(CEnum):
    Off = auto()
    Simple = auto()
    Hardware = auto()


class LightingType(CEnum):
    NoLighting = auto()
    Ambient = auto()
    Point = auto()


class Lighting(Structure):
    mode = EnumField(LightingMode)
    type = EnumField(LightingType)
    ambient_color = StructField(GXColor)
    diffuse_color = StructField(GXColor)
    radius = f32()
    position = StructField(VEC3)
