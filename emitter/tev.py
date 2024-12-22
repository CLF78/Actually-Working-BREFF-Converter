#!/usr/bin/env python3

# tev.py
# TEV stage definitions

from common.field import *
from common.gx import *

class TEVStageColor(Structure):
    color_selection_a = EnumField(GXTevColorArg, default=GXTevColorArg.OutputColor)
    color_selection_b = EnumField(GXTevColorArg, default=GXTevColorArg.OutputColor)
    color_selection_c = EnumField(GXTevColorArg, default=GXTevColorArg.OutputColor)
    color_selection_d = EnumField(GXTevColorArg, default=GXTevColorArg.OutputColor)


class TEVStageColorOp(Structure):
    color_operation = EnumField(GXTevOp, default=GXTevOp.Add)
    color_bias = EnumField(GXTevBias, default=GXTevBias.Zero)
    color_scale = EnumField(GXTevScale, default=GXTevScale.MultiplyBy1)
    color_clamp = boolean(default=False)
    color_register = EnumField(GXTevRegID, default=GXTevRegID.OutputColor)


class TEVStageAlphaOp(Structure):
    alpha_operation = EnumField(GXTevOpAlpha, default=GXTevOpAlpha.Add)
    alpha_bias = EnumField(GXTevBias, default=GXTevBias.Zero)
    alpha_scale = EnumField(GXTevScale, default=GXTevScale.MultiplyBy1)
    alpha_clamp = boolean(default=False)
    alpha_register = EnumField(GXTevRegIDAlpha, default=GXTevRegIDAlpha.OutputAlpha)


class TEVStageAlpha(Structure):
    alpha_selection_a = EnumField(GXTevAlphaArg, default=GXTevAlphaArg.OutputAlpha)
    alpha_selection_b = EnumField(GXTevAlphaArg, default=GXTevAlphaArg.OutputAlpha)
    alpha_selection_c = EnumField(GXTevAlphaArg, default=GXTevAlphaArg.OutputAlpha)
    alpha_selection_d = EnumField(GXTevAlphaArg, default=GXTevAlphaArg.OutputAlpha)


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
    num_tev_stages = u8(cond=skip_json)

    # Obsolete flag
    flag_clamp = boolean()

    # Number of indirect TEV stages
    indirect_target_stages = u8()

    # TEV Texture value (unsure of purpose)
    textures = ListField(u8(), 4, cond=skip_json)

    # TEV stage colors
    colors = ListField(StructField(TEVStageColor), 4, cond=skip_json)

    # TEV color operations
    colorops = ListField(StructField(TEVStageColorOp), 4, cond=skip_json)

    # TEV stage alphas
    alphas = ListField(StructField(TEVStageAlpha), 4, cond=skip_json)

    # TEV alpha operations
    alphaops = ListField(StructField(TEVStageAlphaOp), 4, cond=skip_json)

    # TEV constant colors
    kcolors = ListField(EnumField(GXTevKColorSel), 4, cond=skip_json)

    # TEV constant alphas
    kalphas = ListField(EnumField(GXTevKAlphaSel), 4, cond=skip_json)

    # Parsed TEV stages
    tev_stages = ListField(StructField(TEVStage), cond=skip_binary) # Handled manually

    def decode(self) -> None:

        # Parse each stage
        for i in range(self.num_tev_stages):
            stage = TEVStage()
            stage.texture = self.textures[i]
            stage.colors = self.colors[i]
            stage.colorop = self.colorops[i]
            stage.alphas = self.alphas[i]
            stage.alphaop = self.alphaops[i]
            stage.constant_color_selection = self.kcolors[i]
            stage.constant_alpha_selection = self.kalphas[i]
            self.tev_stages.append(stage)

        # Do decoding
        super().decode()

    def encode(self) -> None:

        # Set number of TEV stages and cut the list if it exceeds the maximum value
        self.tev_stages = self.tev_stages[:4]
        self.num_tev_stages = len(self.tev_stages)

        # Unpack each stage into the fields
        for data in self.tev_stages:
            self.textures.append(data.texture)
            self.colors.append(data.colors)
            self.colorops.append(data.colorop)
            self.alphas.append(data.alphas)
            self.alphaops.append(data.alphaop)
            self.kcolors.append(data.constant_color_selection)
            self.kalphas.append(data.constant_alpha_selection)

        # Fill the remaining slots with dummy data
        for _ in range(len(self.tev_stages), 4):
            self.textures.append(0)
            self.colors.append(TEVStageColor(self))
            self.colorops.append(TEVStageColorOp(self))
            self.alphas.append(TEVStageAlpha(self))
            self.alphaops.append(TEVStageAlphaOp(self))
            self.kcolors.append(GXTevKColorSel.Constant1_1)
            self.kalphas.append(GXTevKAlphaSel.Constant1_1)

        # Do encoding
        super().encode()
