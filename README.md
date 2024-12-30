# Actually-Working-BREFF-Converter
Actually-Working-BREFF-Converter is a Python-based tool for converting BREFF files to JSON and back. The program was created out of frustration with the incomplete support by existing tools, hence its name.

## Functionality
When decoding a BREFF file, the resulting output is a directory containing a series of JSON files. Each effect is saved separately for organizational purposes. A `meta.json` file is included in the directory, containing additional metadata such as the file version and project name.

The encoding process does not guarantee 100% matching data:
- The effects within the BREFF are sorted by name, which is not guaranteed to be the same order as the original file.
- Some tables are optimized to deduplicate entries, leading to different file sizes.
- Unused fields that contain garbage data are ignored during decoding, leading to slight differences in the data.

The program currently does not validate input data, therefore use it with caution to avoid corrupted outputs.

## Compatibility
The tool has been successfully tested against:
- Mario Kart Wii BREFF files (v9)
- New Super Mario Bros. Wii BREFF files (v11)
- NW4R SDK sample files (v10 and v11)

If you find any file to be incompatible, please open an issue and attach it!

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/CLF78/Actually-Working-BREFF-Converter.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Actually-Working-BREFF-Converter
   ```

3. Ensure Python 3.11 or greater is installed.
4. Optionally, install `orjson` to speed up JSON parsing:

   ```bash
   pip install orjson
   ```

## Usage
Run the converter with the following command:

```batch
python3 breff_converter.py <operation> <inputs> [OPTIONS]
```

### Arguments
- `<operation>`: The operation to perform. Can be:
  - `decode`: Convert BREFF files to JSON.
  - `encode`: Convert JSON back to BREFF.
- `<inputs>`: A list of files or folders:
  - For `decode`: One or more BREFF files to be converted to JSON directories.
  - For `encode`: One or more directories containing JSON files to be converted back to BREFF.

### Options
- `-d`, `--dest <paths>`: Paths to the output files or folders for each input.
  - For `decode`, the directories where the JSON files will be created.
  - For `encode`, the paths of the encoded BREFF files.
  - If not specified, the program will append or strip the `.d` extension automatically.
- `-o`, `--overwrite`: Force overwrite the destination files/directories. Without this option, the tool will prevent overwriting existing data.
- `-v`, `--verbose`: Enable verbose output, used for debugging purposes.

### Examples
1. Decode a BREFF file:

   ```bash
   python3 breff_converter.py decode input.breff
   ```

2. Encode a directory of JSON files:

   ```bash
   python3 breff_converter.py encode input.breff.d
   ```

3. Decode multiple BREFF files at once:

   ```bash
   python3 breff_converter.py decode file1.breff file2.breff file3.breff
   ```

4. Specify custom output locations:

   ```bash
   python3 breff_converter.py decode file1.breff file2.breff -d out1 out2
   ```

5. Force overwrite existing destination files:

   ```bash
   python3 breff_converter.py encode input.breff.d -o
   ```

## Changelog
See the [CHANGELOG](CHANGELOG.md) file for details.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Future Plans
This tool is still under development. Future plans include:
- Implement basic data validation.
- Update public documentation of the format.
- Add support for BREFT file parsing (unlikely).
