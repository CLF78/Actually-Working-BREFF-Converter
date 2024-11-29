#!/usr/bin/env python3

# color_input.py
# ColorInput structure

from enum import auto
from common.common import CEnum
from common.field import *

class RasterColor(CEnum):
    Null = 0
    Lighting = auto()


class TevColor(CEnum):
    Null = auto()
    Color1Primary = auto()
    Color1Secondary = auto()
    Color2Primary = auto()
    Color2Secondary = auto()
    Color1Multiply = auto()
    Color2Multiply = auto()


class ColorInput(Structure):
    ras_color = EnumField(RasterColor)
    tev_color1 = EnumField(TevColor)
    tev_color2 = EnumField(TevColor)
    tev_color3 = EnumField(TevColor)
    tev_k_color1 = EnumField(TevColor)
    tev_k_color2 = EnumField(TevColor)
    tev_k_color3 = EnumField(TevColor)
    tev_k_color4 = EnumField(TevColor)
