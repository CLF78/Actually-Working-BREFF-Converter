#!/usr/bin/env python3

# particle.py
# Particle entry definition

from common.field import *
from common.gx import *
from common.nw4r import VEC2, VEC3
from particle.texture import ParticleTextures


class ParticleData(Structure):

    # Size of particle
    data_size = u32(cond=skip_json)

    # Colors
    color1_primary = StructField(GXColor)
    color1_secondary = StructField(GXColor)
    color2_primary = StructField(GXColor)
    color2_secondary = StructField(GXColor)

    # Scale / Rotation / Translation
    particle_size = StructField(VEC2)
    particle_scale = StructField(VEC2)
    particle_rotation = StructField(VEC3)

    # Mostly texture-specific data
    textures = StructField(ParticleTextures, True, alignment=4)

    def encode(self) -> None:
        super().encode()
        self.data_size = self.size()
