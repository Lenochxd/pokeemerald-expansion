import os

for root, dirs, files in os.walk("data"):
    for file in files:
        if file.endswith(".inc") and file.endswith("_backup.inc"):
            inc_path = os.path.join(root, file)
            original_path = inc_path.replace("_backup.inc", ".inc")
            pory_path = inc_path.replace("_backup.inc", ".pory")
            
            if os.path.exists(original_path):
                os.remove(original_path)
            
            os.rename(inc_path, original_path)
            
            if os.path.exists(pory_path):
                os.remove(pory_path)
