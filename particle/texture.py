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
    name = string()


class ParticleTextures(Structure):

    # Texture scales
    texture_scales = ListField(StructField(VEC2), 3, skip_json=True)

    # Texture rotations
    texture_rotations = ListField(f32(), 3, skip_json=True)

    # Texture translations
    texture_translations = ListField(StructField(VEC2), 3, skip_json=True)

    # Texture wrap / reverse flags
    texture_wrap = u16('12xH', skip_json=True)
    texture_reverse = u8(skip_json=True)

    # Alpha compare values
    alpha_compare_value0 = u8(skip_json=True)
    alpha_compare_value1 = u8(skip_json=True)

    # Rotation offsets
    rotate_offset_randoms = ListField(u8(), 3, skip_json=True)
    rotate_offsets = ListField(f32(), 3, skip_json=True)

    # Texture names
    texture_names = ListField(StructField(NameString), 3, skip_json=True)

    # Parsed data for prettier output
    textures = ListField(StructField(ParticleTexture), skip_binary=True)

    def to_json(self) -> dict:

        # Parse each texture
        self.textures.clear()
        for i in range(3):
            texture = ParticleTexture()
            texture.scale = self.texture_scales[i][1]
            texture.rotation = self.texture_rotations[i][1]
            texture.translation = self.texture_translations[i][1]
            texture.wrapS = GXTexWrapMode((self.texture_wrap >> (i * 4)) & 3)
            texture.wrapT = GXTexWrapMode((self.texture_wrap >> (i * 4 + 2)) & 3)
            texture.reverse_mode = ReverseMode((self.texture_reverse >> (i * 2)) & ReverseMode.Mask)
            texture.rotation_offset_random = self.rotate_offset_randoms[i][1]
            texture.rotation_offset = self.rotate_offsets[i][1]
            texture.name = self.texture_names[i][1].name
            self.textures.append((type(texture), texture))

        return super().to_json()

    def to_bytes(self) -> bytes:

        # Cut the list if it exceeds the maximum texture count
        # TODO use validation and bail instead of slicing
        if len(self.textures) > 3:
            self.textures = self.textures[:3]

        # Unpack each texture into the fields
        for i, data in enumerate(self.textures):
            tex_name = NameString(self)
            tex_name.name = data.name

            self.texture_scales.append((ParticleTextures.texture_scales.item_field, data.scale))
            self.texture_rotations.append((ParticleTextures.texture_rotations.item_field, data.rotation))
            self.texture_translations.append((ParticleTextures.texture_translations.item_field, data.translation))
            self.texture_wrap |= (data.wrapS << i * 4)
            self.texture_wrap |= (data.wrapT << i * 4 + 2)
            self.texture_reverse |= (data.reverse_mode << i * 2)
            self.rotate_offset_randoms.append((ParticleTextures.rotate_offset_randoms, data.rotation_offset_random))
            self.rotate_offsets.append((ParticleTextures.rotate_offsets, data.rotation_offset))
            self.texture_names.append((ParticleTextures.texture_names.item_field), tex_name)

        return super().to_bytes()
