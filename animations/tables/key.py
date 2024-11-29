#!/usr/bin/env python3

# key.py
# Animation key frame table definitions

from enum import auto
from common.common import CEnum
from common.field import *

class KeyType(CEnum):
    Fixed = auto()  # Use data embedded in the key frame
    Range  = auto() # Use random clamping on the data at the given index in the range table
    Random = auto() # Pick a random range from the random table and use it for clamping


class KeyCurveType(CEnum):
    Linear = auto()
    Hermite = auto()
    Step = auto()


class KeyFrameBase(Structure):
    frame = u16()
    value_type = EnumField(KeyType, 'Bx')


class KeyFrameTable(Structure):
    entry_count = u16('H2x')
