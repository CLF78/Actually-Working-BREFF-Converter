#!/usr/bin/env python3

# effect.py
# Effect entry definitions

from dataclasses import dataclass

from common.common import BaseBinary, fieldex
from emitter.emitter import EmitterData
from particle.particle import ParticleData
from animations.anim_table import Animations

@dataclass
class Effect(BaseBinary):
    emitter: EmitterData = fieldex()
    particle: ParticleData = fieldex()
    animations: Animations = fieldex(unroll_content=True)
