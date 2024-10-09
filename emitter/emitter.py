#!/usr/bin/env python3

# emitter.py
# Emitter entry definitions

from dataclasses import dataclass

from common.common import BaseBinary, fieldex
from common.gx import *
from common.nw4r import VEC3, MTX23
from emitter.alpha_swing import AlphaSwing
from emitter.color_input import ColorInput
from emitter.flags import CommonFlag, EmitterFlags, DrawFlag
from emitter.lighting import Lighting
from emitter.options import ParticleType, Options
from emitter.params import Params
from emitter.tev import TEVStages


@dataclass
class EmitterData(BaseBinary):

    # Size of emitter
    data_size: int = fieldex('4xI', ignore_json=True)

    # Various flags
    common_flags: CommonFlag = fieldex('I')

    # Emitter shape and other flags
    emitter_flags: EmitterFlags = fieldex(unroll_content=True)

    # Maximum emit time
    emit_lifetime: int = fieldex('H')

    # Particle lifetime
    particle_lifetime: int = fieldex('H')

    # Particle lifetime randomness
    particle_lifetime_randomness: int = fieldex('b')

    # Ratio of the influence on the Following child particle's translation
    inherit_child_particle_translate: int = fieldex('b')

    # Emission interval randomness
    emission_interval_randomness: int = fieldex('b')

    # Emission volume randomness
    emission_volume_randomness: int = fieldex('b')

    # Emission volume
    emission_volume: float = fieldex('f')

    # Emit start time
    emission_start_time: int = fieldex('H')

    # Calculate Elapsed Frames value
    emission_past: int = fieldex('H')

    # Emission interval
    emission_interval: int = fieldex('H')

    # Ratio of the effect on translation of an inherited particle
    inherit_particle_translate: int = fieldex('b')

    # Ratio of the influence on the Following child emitter's translation
    inherit_child_emit_translate: int = fieldex('b')

    # Various shape-specific parameters
    shape_params: Params = fieldex()

    # Number of divisions when the emitter shape is equally spaced
    shape_divisions: int = fieldex('H')

    # Initial velocity randomness
    initial_velocity_randomness: int = fieldex('b')

    # Initial momentum randomness
    initial_momentum_randomness: int = fieldex('b')

    # Speed in all directions
    speed: float = fieldex('f')

    # Y-axis diffusion speed
    y_diffusion_speed: float = fieldex('f')

    # Random direction speed
    random_dir_speed: float = fieldex('f')

    # Normal direction speed
    normal_dir_speed: float = fieldex('f')

    # Normal direction diffusion angle
    normal_dir_diffusion_angle: float = fieldex('f')

    # Specified direction emission speed
    specified_dir_emission_speed: float = fieldex('f')

    # Specified direction diffusion angle
    specified_dir_diffusion_angle: float = fieldex('f')

    # Specified direction
    specified_dir: VEC3 = fieldex()

    # Scale / Rotation / Translation
    scale: VEC3 = fieldex()
    rotation: VEC3 = fieldex()
    translation: VEC3 = fieldex()

    # Near plane for LOD
    near_lod_plane: int = fieldex('b')

    # Far plane for LOD
    far_lod_plane: int = fieldex('b')

    # Minimum generation rate of LOD
    min_lod_emit_rate: int = fieldex('b')

    # LOD alpha
    lod_alpha: int = fieldex('b')

    # Random seed
    random_seed: int = fieldex('I')

    # User data
    user_data: int = fieldex('Q')

    # Draw flag
    draw_flags: DrawFlag = fieldex('H')

    # Alpha compare operations and operator
    alpha_compare_1: GXCompare = fieldex('b')
    alpha_compare_2: GXCompare = fieldex('b')
    alpha_compare_operator: GXAlphaOp = fieldex('b')

    # TEV stages
    tev_stages: TEVStages = fieldex(unroll_content=True)

    # Blend information
    blend_type: GXBlendMode = fieldex('b')
    blend_src_factor: GXBlendFactor = fieldex('b')
    blend_dst_factor: GXBlendFactor = fieldex('b')
    blend_operation: GXLogicOp = fieldex('b')

    # Color and alpha inputs
    color_input: ColorInput = fieldex()
    alpha_input: ColorInput = fieldex()

    # Z Compare Function
    z_compare_func: GXCompare = fieldex('b')

    # Alpha swing type
    alpha_swing: AlphaSwing = fieldex()

    # Lighting
    lighting: Lighting = fieldex()

    # Indirect texture matrix and scale
    indirect_texture_matrix: MTX23 = fieldex()
    indirect_texture_scale: int = fieldex('b')

    # Pivots
    pivot_x: int = fieldex('b')
    pivot_y: int = fieldex('bx')

    # Options
    particle_type: ParticleType = fieldex('B')
    particle_options: Options = fieldex()

    # Z Offset
    z_offset: float = fieldex('f')
