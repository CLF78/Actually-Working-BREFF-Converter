#!/usr/bin/env python3

# texture.py
# Particle texture definitions

from dataclasses import dataclass

from common.common import BaseBinary, CEnum
from common.gx import *
from common.nw4r import VEC2

class ReverseMode(CEnum):
    NoReverse = auto()
    Horizontal = auto()
    Vertical = auto()
    Both = auto()
    Mask = 3


class ParticleTexture(Structure):
    scale = StructField(VEC2)
    rotation = f32()
    translation = StructField(VEC2)
    wrapS = EnumField(GXTexWrapMode)
    wrapT = EnumField(GXTexWrapMode)
    reverse_mode = EnumField(ReverseMode)
    rotation_offset_random = u32()
    rotation_offset = f32()
    name = string()


class ParticleTextures(Structure):

    # Texture scales
    texture_scale1 = StructField(VEC2, skip_json=True)
    texture_scale2 = StructField(VEC2, skip_json=True)
    texture_scale3 = StructField(VEC2, skip_json=True)

    # Texture rotations
    texture_rotation1 = f32(skip_json=True)
    texture_rotation2 = f32(skip_json=True)
    texture_rotation3 = f32(skip_json=True)

    # Texture translations
    texture_translate1 = StructField(VEC2, skip_json=True)
    texture_translate2 = StructField(VEC2, skip_json=True)
    texture_translate3 = StructField(VEC2, skip_json=True)

    # Texture wrap / reverse flags
    texture_wrap = u16('12xH', skip_json=True)
    texture_reverse = u8(skip_json=True)

    # Alpha compare values
    alpha_compare_value0 = u8(skip_json=True)
    alpha_compare_value1 = u8(skip_json=True)

    # Rotation offsets
    rotate_offset_random1 = u8(skip_json=True)
    rotate_offset_random2 = u8(skip_json=True)
    rotate_offset_random3 = u8(skip_json=True)
    rotate_offset1 = f32(skip_json=True)
    rotate_offset2 = f32(skip_json=True)
    rotate_offset3 = f32(skip_json=True)

    # Texture names
    texture_name_len1 = u16(skip_json=True)
    texture_name1 = string(skip_json=True)
    texture_name_len2 = u16(skip_json=True)
    texture_name2 = string(skip_json=True)
    texture_name_len3 = u16(skip_json=True)
    texture_name3 = string(skip_json=True)

    # Parsed data for prettier output
    textures = ListField(StructField(ParticleTexture), skip_binary=True)

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
            self.textures.append((type(texture), texture))

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
