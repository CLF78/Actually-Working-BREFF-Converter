#!/usr/bin/env python3

# key_table.py
# Keyframe table definitions

from enum import auto
from dataclasses import dataclass
from common.common import BaseBinary, CEnum, fieldex

class KeyType(CEnum):
    Fixed = auto()  # Use data embedded in the key frame
    Range  = auto() # Use random clamping on the data at the given index in the range table
    Random = auto() # Pick a random entry from the random table


class KeyCurveType(CEnum):
    Linear = auto()
    Hermite = auto()
    Step = auto()


@dataclass
class KeyFrameBase(BaseBinary):
    frame: int = fieldex('H')
    value_type: KeyType = fieldex('Bx')

    # Curve type values are not listed here because they are used differently by each animation
    param: BaseBinary = fieldex()


@dataclass
class KeyFrameTable(BaseBinary):
    entry_count: int = fieldex('H2x')
    entries: list[KeyFrameBase] = fieldex(ignore_binary=True)
