#!/usr/bin/env python3

# alpha_swing.py
# Alpha swing structure

from enum import auto
from common.common import CEnum
from common.field import *

class AlphaSwingType(CEnum):
    NoSwing = auto()
    Triangle = auto()
    Sawtooth1 = auto()
    Sawtooth2 = auto()
    Square = auto()
    Sine = auto()


class AlphaSwing(Structure):
    type = EnumField(AlphaSwingType)
    cycle_period = u16()
    randomness = s8()
    amplitude = s8()
