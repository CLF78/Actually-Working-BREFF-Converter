#!/usr/bin/env python3

# key.py
# Animation key frame table definitions

from enum import auto
from dataclasses import dataclass
from common.common import BaseBinary, CEnum, fieldex

class KeyType(CEnum):
    Fixed = auto()  # Use data embedded in the key frame
    Range  = auto() # Use random clamping on the data at the given index in the range table
    Random = auto() # Pick a random range from the random table and use it for clamping


class KeyCurveType(CEnum):
    Linear = auto()
    Hermite = auto()
    Step = auto()


@dataclass
class KeyFrameBase(BaseBinary):
    frame: int = fieldex('H')
    value_type: KeyType = fieldex('Bx')


@dataclass
class KeyFrameTable(BaseBinary):
    entry_count: int = fieldex('H2x')
    entries: list[KeyFrameBase] = fieldex(ignore_binary=True)
