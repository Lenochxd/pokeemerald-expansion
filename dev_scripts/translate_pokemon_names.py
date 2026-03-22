#!/usr/bin/env python3
"""
Script to generate French translations of Pokemon species info files.
Reads from localization/pokedex.json and generates localized/gen_X_families_fr.h files
with French Pokemon names.
"""

import json
import re
import os
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
POKEDEX_FILE = REPO_ROOT / "localization" / "pokedex.json"
SPECIES_INFO_DIR = REPO_ROOT / "src" / "data" / "pokemon" / "species_info"
OUTPUT_DIR = REPO_ROOT / "src" / "data" / "pokemon" / "species_info"

# Generations to process (up to gen 8 as per user request)
GENERATIONS = list(range(1, 9))

def load_pokedex():
    """Load Pokemon data from pokedex.json"""
    with open(POKEDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_name_mapping(pokedex_data):
    """Create a mapping of English names to French names by Pokemon ID"""
    mapping = {}
    for pokemon_id, entry in pokedex_data.items():
        english_name = entry['name']['english']
        french_name = entry['name']['french']
        mapping[int(pokemon_id)] = {
            'english': english_name,
            'french': french_name
        }
    return mapping

def read_species_file(gen):
    """Read the species info file for a generation"""
    filename = f"gen_{gen}_families.h"
    filepath = SPECIES_INFO_DIR / filename
    
    if not filepath.exists():
        print(f"Warning: {filepath} does not exist, skipping generation {gen}")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def replace_pokemon_names(content, name_mapping):
    """Replace English Pokemon names with French names in the file content"""
    modified = content
    
    # Pattern to match .speciesName = _("Name") 
    # This regex captures the quoted name and replaces it with the French equivalent
    def replacer(match):
        english_name = match.group(1)
        
        # Try to find the French equivalent
        for pokemon_id, names in name_mapping.items():
            if names['english'] == english_name:
                french_name = names['french']
                return f'.speciesName = _("{french_name}")'
        
        # If not found, return the original (shouldn't happen if data is consistent)
        return match.group(0)
    
    # Match .speciesName = _("...") pattern
    pattern = r'\.speciesName = _\("([^"]+)"\)'
    modified = re.sub(pattern, replacer, modified)
    
    return modified

def generate_french_file(gen, name_mapping):
    """Generate French version of species file for a generation"""
    # Read original file
    content = read_species_file(gen)
    if content is None:
        return False
    
    # Replace names
    french_content = replace_pokemon_names(content, name_mapping)
    
    # Write to output file
    output_filename = f"localized/gen_{gen}_families_fr.h"
    output_filepath = OUTPUT_DIR / output_filename
    
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(french_content)
    
    print(f"Generated: {output_filepath}")
    return True

def main():
    """Main function"""
    print(f"Loading pokedex from {POKEDEX_FILE}...")
    pokedex_data = load_pokedex()
    print(f"Loaded {len(pokedex_data)} Pokemon entries")
    
    name_mapping = create_name_mapping(pokedex_data)
    print(f"Created name mapping for {len(name_mapping)} Pokemon")
    
    print(f"\nGenerating French species files...")
    for gen in GENERATIONS:
        if generate_french_file(gen, name_mapping):
            pass  # Already printed in function
    
    print("\nDone! French species files have been generated.")
    print("You can now use LANGUAGE=FR in the Makefile to build with French names.")

if __name__ == "__main__":
    main()
