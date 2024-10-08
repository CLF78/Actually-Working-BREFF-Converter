#!/usr/bin/env python3

# colorinput.py
# ColorInput definitions

from enum import Enum, auto
from dataclasses import dataclass, field
from common import BaseBinary, STRUCT

class RasterColor(Enum):
    Null = 0
    Lighting = auto()


class TevColor(Enum):
    Null = 0
    Color1Primary = auto()
    Color1Secondary = auto()
    Color2Primary = auto()
    Color2Secondary = auto()
    Color1Multiply = auto()
    Color2Multiply = auto()


@dataclass
class ColorInput(BaseBinary):
    ras_color: RasterColor = field(default=0, metadata=STRUCT('B'))
    tev_color1: TevColor = field(default=0, metadata=STRUCT('B'))
    tev_color2: TevColor = field(default=0, metadata=STRUCT('B'))
    tev_color3: TevColor = field(default=0, metadata=STRUCT('B'))
    tev_k_color1: TevColor = field(default=0, metadata=STRUCT('B'))
    tev_k_color2: TevColor = field(default=0, metadata=STRUCT('B'))
    tev_k_color3: TevColor = field(default=0, metadata=STRUCT('B'))
    tev_k_color4: TevColor = field(default=0, metadata=STRUCT('B'))
