#!/usr/bin/env python3

# texture.py
# Particle texture definitions

from common.common import CEnum
from common.gx import *
from common.nw4r import NameString, VEC2

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
    name = StructField(NameString, unroll=True)


class ParticleTextures(Structure):

    # Texture scales
    texture_scales = ListField(StructField(VEC2), 3, cond=skip_json)

    # Texture rotations
    texture_rotations = ListField(f32(), 3, cond=skip_json)

    # Texture translations
    texture_translations = ListField(StructField(VEC2), 3, cond=skip_json)

    # Texture wrap / reverse flags
    texture_wrap = u16('12xH', cond=skip_json)
    texture_reverse = u8(cond=skip_json)

    # Alpha compare values
    alpha_compare_value0 = u8(cond=skip_json)
    alpha_compare_value1 = u8(cond=skip_json)

    # Rotation offsets
    rotate_offset_randoms = ListField(u8(), 3, cond=skip_json)
    rotate_offsets = ListField(f32(), 3, cond=skip_json)

    # Texture names
    texture_names = ListField(StructField(NameString), 3, cond=skip_json)

    # Parsed data for prettier output
    textures = ListField(StructField(ParticleTexture), cond=skip_binary)

    def to_json(self) -> dict:

        # Assemble each texture
        for i in range(3):
            texture = ParticleTexture()
            texture.scale = self.texture_scales[i]
            texture.rotation = self.texture_rotations[i]
            texture.translation = self.texture_translations[i]
            texture.wrapS = GXTexWrapMode((self.texture_wrap >> (i * 4)) & 3)
            texture.wrapT = GXTexWrapMode((self.texture_wrap >> (i * 4 + 2)) & 3)
            texture.reverse_mode = ReverseMode((self.texture_reverse >> (i * 2)) & ReverseMode.Mask)
            texture.rotation_offset_random = self.rotate_offset_randoms[i]
            texture.rotation_offset = self.rotate_offsets[i]
            texture.name = self.texture_names[i]
            self.textures.append(texture)

        # Let the parser do the rest
        return super().to_json()

    def to_bytes(self) -> bytes:

        # Cut the list if it exceeds the maximum texture count
        # TODO use validation and bail instead of slicing
        if len(self.textures) > 3:
            self.textures = self.textures[:3]

        # Unpack each texture into the respective fields
        for i, data in enumerate(self.textures):
            self.texture_scales.append(data.scale)
            self.texture_rotations.append(data.rotation)
            self.texture_translations.append(data.translation)
            self.texture_wrap |= (data.wrapS << i * 4)
            self.texture_wrap |= (data.wrapT << i * 4 + 2)
            self.texture_reverse |= (data.reverse_mode << i * 2)
            self.rotate_offset_randoms.append(data.rotation_offset_random)
            self.rotate_offsets.append(data.rotation_offset)
            self.texture_names.append(data.name)

        # Let the parser do the rest
        return super().to_bytes()
