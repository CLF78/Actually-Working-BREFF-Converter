#!/usr/bin/env python3

# alpha_swing.py
# Alpha swing structure

from enum import auto
from dataclasses import dataclass
from common.common import BaseBinary, CEnum, fieldex

class AlphaSwingType(CEnum):
    NoSwing = auto()
    Triangle = auto()
    Sawtooth1 = auto()
    Sawtooth2 = auto()
    Square = auto()
    Sine = auto()


@dataclass
class AlphaSwing(BaseBinary):
    type: AlphaSwingType = fieldex('b')
    cycle_period: int = fieldex('H')
    randomness: int = fieldex('b')
    amplitude: int = fieldex('b')
