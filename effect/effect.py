#!/usr/bin/env python3

# effect.py
# Effect entry definitions

from dataclasses import dataclass, Field

from common.common import BaseBinary, fieldex
from emitter.emitter import EmitterData
from particle.particle import ParticleData
from animations.anim_table import Animations

@dataclass
class EffectData(BaseBinary):
    emitter: EmitterData = fieldex()
    particle: ParticleData = fieldex()
    animations: Animations = fieldex(unroll_content=True)


@dataclass
class Effect(BaseBinary):
    name_len: int = fieldex('H', ignore_json=True)
    name: str = fieldex()
    data_offset: int = fieldex('I', ignore_json=True)
    data_size: int = fieldex('I', ignore_json=True)
    data: EffectData = fieldex(ignore_binary=True, unroll_content=True)

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
