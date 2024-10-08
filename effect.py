#!/usr/bin/env python3

# effect.py
# Effect entry definitions

from dataclasses import dataclass, field, Field

from common import BaseBinary, IGNORE_BINARY, IGNORE_JSON, STRUCT, UNROLL_CONTENT
from emitter.emitter import EmitterData

@dataclass
class EffectData(BaseBinary):
    emitter: EmitterData = None


@dataclass
class Effect(BaseBinary):
    name_len: int = field(default=0, metadata=IGNORE_JSON | STRUCT('H'))
    name: str = ''
    data_offset: int = field(default=0, metadata=IGNORE_JSON | STRUCT('I'))
    data_size: int = field(default=0, metadata=IGNORE_JSON | STRUCT('I'))
    data: EffectData = field(kw_only=True, default=None, metadata=IGNORE_BINARY | UNROLL_CONTENT)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'Effect':

        # Get effect
        effect = super().from_bytes(data, offset, parent)
        effect.data = EffectData.from_bytes(data, effect.parent.offset + effect.data_offset, effect)
        return effect

    def to_bytes(self) -> bytes:
        self.name_len = len(self.name) + 1
        self.data_size = self.data.size()
        return super().to_bytes()

    # TODO check for minimum length
    def validate(self, max_length: int, field: Field) -> None:
        return
