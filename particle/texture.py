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
    name = StructField(NameString, unroll=True)
    scale = StructField(VEC2)
    rotation = f32()
    translation = StructField(VEC2)
    wrapS = EnumField(GXTexWrapMode)
    wrapT = EnumField(GXTexWrapMode)
    reverse_mode = EnumField(ReverseMode)
    rotation_offset_random = u32()
    rotation_offset = f32()


class ParticleTextures(Structure):

    # Texture scales
    texture_scales = ListField(StructField(VEC2), 3, cond=skip_json)

    # Texture rotations
    texture_rotations = ListField(f32(), 3, cond=skip_json)

    # Texture translations
    texture_translations = ListField(StructField(VEC2), 3, cond=skip_json)

    # Texture wrap / reverse flags
    texture_wrap = u16('12xH', default=0, cond=skip_json)
    texture_reverse = u8(default=0, cond=skip_json)

    # Alpha compare values
    alpha_compare_value0 = u8()
    alpha_compare_value1 = u8()

    # Rotation offsets
    rotate_offset_randoms = ListField(u8(), 3, cond=skip_json)
    rotate_offsets = ListField(f32(), 3, cond=skip_json)

    # Texture names
    texture_names = ListField(StructField(NameString), 3, cond=skip_json)

    # Parsed data for prettier output
    textures = ListField(StructField(ParticleTexture), cond=skip_binary)

    def decode(self) -> None:

        # Skip entries with empty texture names
        for i in range(3):
            if not self.texture_names[i].name:
                continue

            # Assemble the texture
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

        # Do decoding
        super().decode()

    def encode(self) -> None:

        # Cut the list if it exceeds the maximum texture count
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

        # Fill any remaining entries with dummy data
        for _ in range(len(self.texures), 3):
            dummy_scale = VEC2(self)
            dummy_scale.x = dummy_scale.y = 1.0
            dummy_name = NameString(self)
            dummy_name.name = ''
            dummy_trans = VEC2(self)
            dummy_trans.x = dummy_trans.y = 0.0

            self.texture_scales.append(dummy_scale)
            self.texture_rotations.append(0.0)
            self.texture_translations.append(dummy_trans)
            self.rotate_offset_randoms.append(0)
            self.rotate_offsets.append(0.0)
            self.texture_names.append(dummy_name)

        # Do encoding
        super().encode()
