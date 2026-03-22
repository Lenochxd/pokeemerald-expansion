# Pokemon Name Localization Guide

This guide explains how to build pokeemerald-expansion with different language settings.

## Quick Start

### Building with English names (default):
```bash
make rom
# or explicitly
make rom LANGUAGE=EN
```

### Building with French names:
```bash
make rom LANGUAGE=FR
```

## How It Works

### Files Generated
The translation script (`dev_scripts/translate_pokemon_names.py`) automatically generates French translation files for all 8 generations:
- `src/data/pokemon/species_info/gen_1_families_fr.h`
- `src/data/pokemon/species_info/gen_2_families_fr.h`
- ... up to ...
- `src/data/pokemon/species_info/gen_8_families_fr.h`

### Build System
1. The Makefile accepts a `LANGUAGE` variable (default: `EN`)
2. When `LANGUAGE=FR` is set, the compiler flag `-DLANGUAGE_FR` is added
3. `src/data/pokemon/species_info.h` conditionally includes either:
   - English files: `gen_X_families.h`
   - French files: `gen_X_families_fr.h` (when `LANGUAGE_FR` is defined)

## Regenerating French Files

If you modify the pokedex.json file or want to regenerate the French files:

```bash
# From the project root
python dev_scripts/translate_pokemon_names.py
```

This will regenerate all `gen_X_families_fr.h` files based on the French names in `localization/pokedex.json`.

## Adding More Languages

To add support for additional languages:

1. Add French names in `localization/pokedex.json` (already done)
2. Update `dev_scripts/translate_pokemon_names.py` to support the new language:
   - Modify `GENERATIONS` if needed
   - Update the `create_name_mapping()` function to extract the language names
   - Generate the files with the appropriate suffix

3. Modify `src/data/pokemon/species_info.h` to include conditional includes for the new language

4. Update the Makefile to pass the appropriate preprocessor flag

## Example: Adding Chinese Support

1. Edit `dev_scripts/translate_pokemon_names.py`:
```python
def create_name_mapping(pokedex_data):
    """Create a mapping of English names to all language variants"""
    mapping = {}
    for entry in pokedex_data:
        pokemon_id = entry['id']
        mapping[pokemon_id] = {
            'english': entry['name']['english'],
            'french': entry['name']['french'],
            'chinese': entry['name']['chinese'],  # Add this line
        }
    return mapping

# Then generate Chinese files with a similar replacement function
```

2. Update `species_info.h` to include conditional Chinese files

3. Update Makefile to support `LANGUAGE=ZH` (or similar)

## Verification

To verify the translation is working:
```bash
# Check that French filenames are referenced
grep "speciesName = .*(" src/data/pokemon/species_info/gen_1_families_fr.h | head -5

# Build and test
make rom LANGUAGE=FR
```

## Notes

- Gen 9 files are not translated (kept in English by design, as they were added after French translation data was compiled)
- The `_()` macro in the code is a placeholder for localization that currently just returns the string as-is
- All Pokemon species names, including alternate forms (Mega Evolutions, regional variants, etc.) are translated
