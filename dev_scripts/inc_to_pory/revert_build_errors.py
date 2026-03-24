import os
import re

def revert(file):
    pory_path = os.path.abspath(file)
    backup_path = pory_path.replace(".pory", "_backup.inc")
    compiled_path = pory_path.replace(".pory", ".inc")
    
    if os.path.exists(pory_path):
        os.remove(pory_path)
    if os.path.exists(compiled_path):
        os.remove(compiled_path)
    if os.path.exists(backup_path):
        os.rename(backup_path, compiled_path)
    
    return True

def remove_errors(make_output: str):
    print(f"Processing {len(make_output.splitlines())} lines of make output...")
    
    for line in make_output.splitlines():
        
        result = re.search('tools/poryscript/poryscript -i(.*)-o', line)
        if not result:
            continue
        
        result = result.group(1).strip()
        
        worked = revert(result)
        if worked:
            print(f"Reverted {result} successfully.")

if __name__ == "__main__":
    make_output = input("Path of make output file: ")
    if os.path.exists(make_output):
        with open(make_output, "r") as f:
            make_output_content = f.read()
        remove_errors(make_output_content)
    else:
        print(f"File {make_output} does not exist.")