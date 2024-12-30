# Changelog
All notable changes to this project will be documented in this file.

## 1.0 - 2024-12-30
- Implemented encoding support.
- Added missing flags for Hermite-interpolated keyframes.
- Added missing `speedBasedVertical` option to Billboard particles.
- Fixed incorrect minimum Python version.
- Fixed JSON dumping without `orjson`.
- Fixed incorrect function annotation causing issues with Python >= 3.12.
- Added overwrite argument (the original `-o` option is now `-d`).
- Fixed automatically generated output names.
- Do not treat particle textures as a list and remove empty texture entries from the JSON output.
- Don't hide target options for Speed/Tail Field animations.
- Fixed handling of child parameters in PostField animations.
- Fixed incorrect decoding of Rotate animation targets and random pool entries.
- Restored frame count and frame numbers for init animations.
- Renamed `size` to `scale` in PostField animation parameters to prevent name conflicts.
- Removed some unnecessary default values and fixed some incorrect ones.

## Beta - 2024-12-17
- Initial release (decoding support only).
