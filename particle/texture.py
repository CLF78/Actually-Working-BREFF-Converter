#!/usr/bin/env python3

# texture.py
# Particle texture definitions

from dataclasses import dataclass

from common.common import BaseBinary, CEnum, fieldex
from common.gx import *
from common.nw4r import VEC2

class ReverseMode(CEnum):
    NoReverse = auto()
    Horizontal = auto()
    Vertical = auto()
    Both = auto()
    Mask = 3


@dataclass
class ParticleTexture(BaseBinary):
    scale: VEC2 = fieldex()
    rotation: float = fieldex()
    translation: VEC2 = fieldex()
    wrapS: GXTexWrapMode = fieldex()
    wrapT: GXTexWrapMode = fieldex()
    reverse_mode: ReverseMode = fieldex()
    rotation_offset_random: int = fieldex()
    rotation_offset: float = fieldex()
    name: str = fieldex()


@dataclass
class ParticleTextures(BaseBinary):

    # Texture scales
    texture_scale1: VEC2 = fieldex(ignore_json=True)
    texture_scale2: VEC2 = fieldex(ignore_json=True)
    texture_scale3: VEC2 = fieldex(ignore_json=True)

    # Texture rotations
    texture_rotation1: float = fieldex('f', ignore_json=True)
    texture_rotation2: float = fieldex('f', ignore_json=True)
    texture_rotation3: float = fieldex('f', ignore_json=True)

    # Texture translations
    texture_translate1: VEC2 = fieldex(ignore_json=True)
    texture_translate2: VEC2 = fieldex(ignore_json=True)
    texture_translate3: VEC2 = fieldex(ignore_json=True)

    # Texture wrap / reverse flags
    texture_wrap: int = fieldex('12xH', ignore_json=True)
    texture_reverse: int = fieldex('B', ignore_json=True)

    # Alpha compare values
    alpha_compare_value0: int = fieldex('B', ignore_json=True)
    alpha_compare_value1: int = fieldex('B', ignore_json=True)

    # Rotation offsets
    rotate_offset_random1: int = fieldex('B', ignore_json=True)
    rotate_offset_random2: int = fieldex('B', ignore_json=True)
    rotate_offset_random3: int = fieldex('B', ignore_json=True)
    rotate_offset1: float = fieldex('f', ignore_json=True)
    rotate_offset2: float = fieldex('f', ignore_json=True)
    rotate_offset3: float = fieldex('f', ignore_json=True)

    # Texture names
    texture_name_len1: int = fieldex('H', ignore_json=True)
    texture_name1: str = fieldex(ignore_json=True)
    texture_name_len2: int = fieldex('H', ignore_json=True)
    texture_name2: str = fieldex(ignore_json=True)
    texture_name_len3: int = fieldex('H', ignore_json=True)
    texture_name3: str = fieldex(ignore_json=True)

    # Parsed data for prettier output
    textures: list[ParticleTexture] = fieldex(ignore_binary=True)

    def to_json(self) -> dict:

        # Parse each texture
        self.textures.clear()
        for i in range(3):
            texture = ParticleTexture()
            texture.scale = getattr(self, f'texture_scale{i+1}')
            texture.rotation = getattr(self, f'texture_rotation{i+1}')
            texture.translation = getattr(self, f'texture_translate{i+1}')
            texture.wrapS = GXTexWrapMode((self.texture_wrap >> (i * 4)) & 3)
            texture.wrapT = GXTexWrapMode((self.texture_wrap >> (i * 4 + 2)) & 3)
            texture.reverse_mode = ReverseMode((self.texture_reverse >> (i * 2)) & ReverseMode.Mask.value)
            texture.rotation_offset_random = getattr(self, f'rotate_offset_random{i+1}')
            texture.rotation_offset = getattr(self, f'rotate_offset{i+1}')
            texture.name = getattr(self, f'texture_name{i+1}')
            self.textures.append(texture)

        return super().to_json()

    def to_bytes(self) -> bytes:

        # Cut the list if it exceeds the maximum texture count
        # TODO use validation and bail instead of slicing
        if len(self.textures) > 3:
            self.textures = self.textures[:3]

        # Unpack each texture into the fields
        for i, data in enumerate(self.textures):
            setattr(self, f'texture_scale{i+1}', data.scale)
            setattr(self, f'texture_rotation{i+1}', data.rotation)
            setattr(self, f'texture_translate{i+1}', data.translation)
            self.texture_wrap |= (data.wrapS.value << i * 4)
            self.texture_wrap |= (data.wrapT.value << i * 4 + 2)
            self.texture_reverse |= (data.reverse_mode.value << i * 2)
            setattr(self, f'rotate_offset_random{i+1}', data.rotation_offset_random)
            setattr(self, f'rotate_offset{i+1}', data.rotation_offset)
            setattr(self, f'texture_name_len{i+1}', len(data.name) + 1)
            setattr(self, f'texture_name{i+1}', data.name)

        return super().to_bytes()
