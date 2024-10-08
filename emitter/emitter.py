#!/usr/bin/env python3

# emitter.py
# Emitter entry definitions

from enum import Enum, auto
from dataclasses import dataclass, field

from common import BaseBinary, VEC3, IGNORE_JSON, STRUCT, UNROLL_CONTENT
from emitter.flags import CommonFlag, EmitterFlags, DrawFlag
from emitter.gx import GXCompare, GXAlphaOp, GXBlendMode, GXBlendFactor, GXLogicOp
from emitter.params import Params
from emitter.tev import TEVStages
from emitter.colorinput import ColorInput
from emitter.lighting import Lighting

class AlphaFlickType(Enum):
    NoFlick = 0
    Triangle = auto()
    Sawtooth1 = auto()
    Sawtooth2 = auto()
    Square = auto()
    Sine = auto()


@dataclass
class EmitterData(BaseBinary):

    # Size of emitter
    data_size: int = field(default=0, metadata=IGNORE_JSON | STRUCT('4xI'))

    # Various flags
    common_flag: CommonFlag = field(default=0, metadata=STRUCT('I'))

    # Emitter shape and other flags
    emitter_flags: EmitterFlags = field(default=None, metadata=UNROLL_CONTENT)

    # Maximum emit time
    emit_lifetime: int = field(default=0, metadata=STRUCT('H'))

    # Particle lifetime
    particle_lifetime: int = field(default=0, metadata=STRUCT('H'))

    # Particle lifetime randomness
    particle_lifetime_randomness: int = field(default=0, metadata=STRUCT('b'))

    # Ratio of the influence on the Following child particle's translation
    inherit_child_particle_translate: int = field(default=0, metadata=STRUCT('b'))

    # Emission interval randomness
    emission_interval_randomness: int = field(default=0, metadata=STRUCT('b'))

    # Emission volume randomness
    emission_volume_randomness: int = field(default=0, metadata=STRUCT('b'))

    # Emission volume
    emission_volume: float = field(default=0.0, metadata=STRUCT('f'))

    # Emit start time
    emission_start_time: int = field(default=0, metadata=STRUCT('H'))

    # Calculate Elapsed Frames value
    emission_past: int = field(default=0, metadata=STRUCT('H'))

    # Emission interval
    emission_interval: int = field(default=0, metadata=STRUCT('H'))

    # Ratio of the effect on translation of an inherited particle
    inherit_particle_translate: int = field(default=0, metadata=STRUCT('b'))

    # Ratio of the influence on the Following child emitter's translation
    inherit_child_emit_translate: int = field(default=0, metadata=STRUCT('b'))

    # Various shape-specific parameters
    shape_params: Params = None

    # Number of divisions when the emitter shape is equally spaced
    shape_divisions: int = field(default=0, metadata=STRUCT('H'))

    # Initial velocity randomness
    initial_velocity_randomness: int = field(default=0, metadata=STRUCT('b'))

    # Initial momentum randomness
    initial_momentum_randomness: int = field(default=0.0, metadata=STRUCT('b'))

    # Speed in all directions
    speed: float = field(default=0.0, metadata=STRUCT('f'))

    # Y-axis diffusion speed
    y_diffusion_speed: float = field(default=0.0, metadata=STRUCT('f'))

    # Random direction speed
    random_dir_speed: float = field(default=0.0, metadata=STRUCT('f'))

    # Normal direction speed
    normal_dir_speed: float = field(default=0.0, metadata=STRUCT('f'))

    # Normal direction diffusion angle
    normal_dir_diffusion_angle: float = field(default=0.0, metadata=STRUCT('f'))

    # Specified direction emission speed
    specified_dir_emission_speed: float = field(default=0.0, metadata=STRUCT('f'))

    # Specified direction diffusion angle
    specified_dir_diffusion_angle: float = field(default=0.0, metadata=STRUCT('f'))

    # Specified direction
    specified_dir: VEC3 = None

    # Scale
    scale: VEC3 = None

    # Rotation
    rotation: VEC3 = None

    # Translation
    translation: VEC3 = None

    # Near plane for LOD
    near_lod_plane: int = field(default=0, metadata=STRUCT('B'))

    # Far plane for LOD
    far_lod_plane: int = field(default=0, metadata=STRUCT('B'))

    # Minimum generation rate of LOD
    min_lod_emit_rate: int = field(default=0, metadata=STRUCT('B'))

    # LOD alpha
    lod_alpha: int = field(default=0, metadata=STRUCT('B'))

    # Random seed
    random_seed: int = field(default=0, metadata=STRUCT('I'))

    # User data
    user_data: int = field(default=0, metadata=STRUCT('Q'))

    # Draw flag
    draw_flags: DrawFlag = field(default=0, metadata=STRUCT('H'))

    # Alpha compare operations and operator
    alpha_compare_1: GXCompare = field(default=0, metadata=STRUCT('B'))
    alpha_compare_2: GXCompare = field(default=0, metadata=STRUCT('B'))
    alpha_compare_operator: GXAlphaOp = field(default=0, metadata=STRUCT('B'))

    # TEV stages
    tev_stages: TEVStages = field(default=None, metadata=UNROLL_CONTENT)

    # Blend information
    blend_type: GXBlendMode = field(default=0, metadata=STRUCT('B'))
    blend_src_factor: GXBlendFactor = field(default=0, metadata=STRUCT('B'))
    blend_dst_factor: GXBlendFactor = field(default=0, metadata=STRUCT('B'))
    blend_operation: GXLogicOp = field(default=0, metadata=STRUCT('B'))

    # Color and alpha inputs
    color_input: ColorInput = None
    alpha_input: ColorInput = None

    # Z Compare Function
    z_compare_func: GXCompare = field(default=0, metadata=STRUCT('B'))

    # Alpha swing type
    alpha_swing_type: AlphaFlickType = field(default=0, metadata=STRUCT('B'))

    # Alpha swing cycle period
    alpha_swing_cycle: int = field(default=0, metadata=STRUCT('H'))

    # Alpha swing randomness
    alpha_swing_randomness: int = field(default=0, metadata=STRUCT('B'))

    # Alpha swing amplitude
    alpha_swing_amplitude: int = field(default=0, metadata=STRUCT('B'))

    # Lighting
    lighting: Lighting = None
