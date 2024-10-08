#!/usr/bin/env python3

# colorinput.py
# ColorInput structure

from enum import auto
from dataclasses import dataclass
from common.common import BaseBinary, CEnum, fieldex

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


@dataclass
class ColorInput(BaseBinary):
    ras_color: RasterColor = fieldex('B')
    tev_color1: TevColor = fieldex('B')
    tev_color2: TevColor = fieldex('B')
    tev_color3: TevColor = fieldex('B')
    tev_k_color1: TevColor = fieldex('B')
    tev_k_color2: TevColor = fieldex('B')
    tev_k_color3: TevColor = fieldex('B')
    tev_k_color4: TevColor = fieldex('B')
