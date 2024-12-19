#!/usr/bin/env python3

# emitter.py
# Emitter entry definitions

from common.field import *
from common.gx import *
from common.nw4r import VEC3, MTX23
from emitter.alpha_swing import AlphaSwing
from emitter.color_input import ColorInput
from emitter.flags import CommonFlag, DrawFlag, EmitterFlags, EmitterShape
from emitter.lighting import Lighting
from emitter.options import *
from emitter.params import *
from emitter.tev import TEVStages

class EmitterData(Structure):

    def get_emitter_params(self, _) -> Field:
        match self.emitter_flags.shape:
            case EmitterShape.Point:
                return padding(24)
            case EmitterShape.Disc:
                return StructField(DiscParams)
            case EmitterShape.Line:
                return StructField(LineParams)
            case EmitterShape.Cube:
                return StructField(CubeParams)
            case _:
                return StructField(CylinderSphereTorusParams)


    def get_options(self, _) -> Field:
        match self.particle_type:
            case ParticleType.Billboard:
                return StructField(BillboardOptions)
            case ParticleType.Directional:
                return StructField(DirectionalOptions)
            case ParticleType.Stripe:
                return StructField(StripeOptions)
            case ParticleType.SmoothStripe:
                return StructField(SmoothStripeOptions)
            case _:
                return StructField(PointLineFreeOptions)


    # Size of emitter
    data_size = u32('4xI', cond=skip_json)

    # Various flags
    common_flags = FlagEnumField(CommonFlag, 'I')

    # Emitter shape and other flags
    emitter_flags = StructField(EmitterFlags, unroll=True)

    # Maximum emit time
    emit_lifetime = u16()

    # Particle lifetime
    particle_lifetime = u16()

    # Particle lifetime randomness
    particle_lifetime_randomness = s8()

    # Ratio of the influence on the Following child particle's translation
    inherit_child_particle_translate = s8()

    # Emission interval randomness
    emission_interval_randomness = s8()

    # Emission volume randomness
    emission_volume_randomness = s8()

    # Emission volume
    emission_volume = f32()

    # Emit start time
    emission_start_time = u16()

    # Calculate Elapsed Frames value
    emission_past = u16()

    # Emission interval
    emission_interval = u16()

    # Ratio of the effect on translation of an inherited particle
    inherit_particle_translate = s8()

    # Ratio of the influence on the Following child emitter's translation
    inherit_child_emit_translate = s8()

    # Various shape-specific parameters
    shape_params = UnionField(get_emitter_params)

    # Number of divisions when the emitter shape is equally spaced
    shape_divisions = u16()

    # Initial velocity randomness
    initial_velocity_randomness = s8()

    # Initial momentum randomness
    initial_momentum_randomness = s8()

    # Speed in all directions
    speed = f32()

    # Y-axis diffusion speed
    y_diffusion_speed = f32()

    # Random direction speed
    random_dir_speed = f32()

    # Normal direction speed
    normal_dir_speed = f32()

    # Normal direction diffusion angle
    normal_dir_diffusion_angle = f32()

    # Specified direction emission speed
    specified_dir_emission_speed = f32()

    # Specified direction diffusion angle
    specified_dir_diffusion_angle = f32()

    # Specified direction
    specified_dir = StructField(VEC3)

    # Scale / Rotation / Translation
    scale = StructField(VEC3)
    rotation = StructField(VEC3)
    translation = StructField(VEC3)

    # Near plane for LOD
    near_lod_plane = s8()

    # Far plane for LOD
    far_lod_plane = s8()

    # Minimum generation rate of LOD
    min_lod_emit_rate = s8()

    # LOD alpha
    lod_alpha = s8()

    # Random seed
    random_seed = u32()

    # User data
    user_data = u64()

    # Draw flag
    draw_flags = FlagEnumField(DrawFlag, 'H')

    # Alpha compare operations and operator
    alpha_compare_1 = EnumField(GXCompare)
    alpha_compare_2 = EnumField(GXCompare)
    alpha_compare_operator = EnumField(GXAlphaOp)

    # TEV stages
    tev_stages = StructField(TEVStages, unroll=True)

    # Blend information
    blend_type = EnumField(GXBlendMode)
    blend_src_factor = EnumField(GXBlendFactor)
    blend_dst_factor = EnumField(GXBlendFactor)
    blend_operation = EnumField(GXLogicOp)

    # Color and alpha inputs
    color_input = StructField(ColorInput)
    alpha_input = StructField(ColorInput)

    # Z Compare Function
    z_compare_func = EnumField(GXCompare)

    # Alpha swing type
    alpha_swing = StructField(AlphaSwing)

    # Lighting
    lighting = StructField(Lighting)

    # Indirect texture matrix and scale
    indirect_texture_matrix = StructField(MTX23)
    indirect_texture_scale = s8()

    # Pivots
    pivot_x = s8()
    pivot_y = s8('bx')

    # Options
    particle_type = EnumField(ParticleType)
    particle_options = UnionField(get_options)

    # Z Offset
    z_offset = f32()
