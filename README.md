# Actually-Working-BREFF-Converter
Actually-Working-BREFF-Converter is a Python-based tool for converting BREFF files to JSON and back. The program was created out of frustration with the incomplete support by existing tools, hence its name.

Currently, the program only supports BREFF to JSON conversion, making it a beta release.

## Compatibility
The tool has been successfully tested against:
- Mario Kart Wii BREFF files (v9)
- New Super Mario Bros. Wii BREFF files (v11)
- NW4R SDK sample file (v11)

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

4. Optionally, install `orjson` to speed up parsing:

   ```bash
   pip install orjson
   ```

## Usage
Run the converter with the following command:

```bash
python3 breff_decode.py [OPTIONS] <inputs...>
```

### Arguments
- `<inputs...>`: One or more paths to the BREFF files to be converted.

### Options
- `-o`, `--outputs <paths...>`: Paths to the output directories for each input file. If not specified, output directories will be named after input files with the `.d` extension.
- `-v`, `--verbose`: Enable verbose output for detailed processing logs, used for debugging purposes.

### Examples
1. Convert a single file:

   ```bash
   python3 breff_decode.py input.breff
   ```

2. Convert multiple files:

   ```bash
   python3 breff_decode.py file1.breff file2.breff file3.breff
   ```

3. Specify custom output directories for each input:

   ```bash
   python3 breff_decode.py file1.breff file2.breff -o out1 out2
   ```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Future Plans
This tool is still under development. Future plans include:
- Implement JSON to BREFF conversion
- Implement basic format validation
- Update public documentation of the format
- Add support for BREFT file parsing
