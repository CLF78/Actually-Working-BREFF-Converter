#!/usr/bin/env python3

# particle.py
# Particle entry definition

from dataclasses import dataclass

from common.common import BaseBinary, fieldex
from common.gx import *
from common.nw4r import VEC2, VEC3
from particle.texture import ParticleTextures


@dataclass
class ParticleData(BaseBinary):

    # Size of particle
    data_size: int = fieldex('I', ignore_json=True)

    # Colors
    color1_primary: GXColor = fieldex()
    color1_secondary: GXColor = fieldex()
    color2_primary: GXColor = fieldex()
    color2_secondary: GXColor = fieldex()

    # Scale / Rotation / Translation
    particle_size: VEC2 = fieldex()
    particle_scale: VEC2 = fieldex()
    particle_rotation: VEC3 = fieldex()

    # Mostly texture-specific data
    textures: ParticleTextures = fieldex(unroll_content=True, align_pad=4)
