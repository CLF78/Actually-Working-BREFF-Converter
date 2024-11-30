#!/usr/bin/env python3

# tev.py
# TEV stage definitions

from common.field import *
from common.gx import *

class TEVStageColor(Structure):
    color_selection_a = EnumField(GXTevColorArg)
    color_selection_b = EnumField(GXTevColorArg)
    color_selection_c = EnumField(GXTevColorArg)
    color_selection_d = EnumField(GXTevColorArg)


class TEVStageColorOp(Structure):
    color_operation = EnumField(GXTevOp)
    color_bias = EnumField(GXTevBias)
    color_scale = EnumField(GXTevScale)
    color_clamp = boolean()
    color_register = EnumField(GXTevRegID)


class TEVStageAlphaOp(Structure):
    alpha_operation = EnumField(GXTevOpAlpha)
    alpha_bias = EnumField(GXTevBias)
    alpha_scale = EnumField(GXTevScale)
    alpha_clamp = boolean()
    alpha_register = EnumField(GXTevRegIDAlpha)


class TEVStageAlpha(Structure):
    alpha_selection_a = EnumField(GXTevAlphaArg)
    alpha_selection_b = EnumField(GXTevAlphaArg)
    alpha_selection_c = EnumField(GXTevAlphaArg)
    alpha_selection_d = EnumField(GXTevAlphaArg)


class TEVStage(Structure):
    texture = u32()
    colors = StructField(TEVStageColor, True)
    colorop = StructField(TEVStageColorOp, True)
    alphas = StructField(TEVStageAlpha, True)
    alphaop = StructField(TEVStageAlphaOp, True)
    constant_color_selection = EnumField(GXTevKColorSel)
    constant_alpha_selection = EnumField(GXTevKAlphaSel)


class TEVStages(Structure):

    # Number of TEV stages
    num_tev_stages = u8(skip_json=True)

    # Obsolete flag
    flag_clamp = boolean()

    # Number of indirect TEV stages
    indirect_target_stages = u8()

    # TEV Texture value (unsure of purpose)
    textures = ListField(u8(), 4, skip_json=True)

    # TEV stage colors
    colors = ListField(StructField(TEVStageColor), 4, skip_json=True)

    # TEV color operations
    colorops = ListField(StructField(TEVStageColorOp), 4, skip_json=True)

    # TEV stage alphas
    alphas = ListField(StructField(TEVStageAlpha), 4, skip_json=True)

    # TEV alpha operations
    alphaops = ListField(StructField(TEVStageAlphaOp), 4, skip_json=True)

    # TEV constant colors
    kcolors = ListField(EnumField(GXTevKColorSel), 4, skip_json=True)

    # TEV constant alphas
    kalphas = ListField(EnumField(GXTevKAlphaSel), 4, skip_json=True)

    # Parsed TEV stages
    tev_stages = ListField(StructField(TEVStage), skip_binary=True) # Handled manually

    def to_json(self) -> dict:

        # Parse each stage
        self.tev_stages.clear()
        for i in range(1, self.num_tev_stages + 1):
            stage = TEVStage()
            stage.texture = self.textures[i][1]
            stage.colors = self.colors[i][1]
            stage.colorop = self.colorops[i][1]
            stage.alphas = self.alphas[i][1]
            stage.alphaop = self.alphaops[i][1]
            stage.constant_color_selection = self.kcolors[i][1]
            stage.constant_alpha_selection = self.kalphas[i][1]
            self.tev_stages.append((type(stage), stage))

        # Return result
        return super().to_json()

    def to_bytes(self) -> bytes:

        # Set value
        self.num_tev_stages = len(self.tev_stages)

        # Unpack each stage into the fields
        for data in self.tev_stages:
            self.textures.append((TEVStages.textures.item_field, data.texture))
            self.colors.append((TEVStages.colors.item_field, data.colors))
            self.colorops.append((TEVStages.colorops.item_field, data.colorop))
            self.alphas.append((TEVStages.alphas.item_field, data.alphas))
            self.alphaops.append((TEVStages.alphaops.item_field, data.alphaop))
            self.kcolors.append((TEVStages.kcolors.item_field, data.constant_color_selection))
            self.kalphas.append((TEVStages.kalphas.item_field, data.constant_alpha_selection))

        return super().to_bytes()
