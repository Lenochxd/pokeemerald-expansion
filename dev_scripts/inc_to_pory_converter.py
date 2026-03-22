import os

"""
this script converts .inc files to .pory files, which are used by poryscript.
It checks for the "DO NOT MODIFY" warning and skips those files, as well as empty files or files that are already in pory format.
After converting, it deletes the original .inc file.

update: do not use this, I think it's stupid and would be better to just convert the needed files manually.
I see no purpose in converting all .inc files to .pory with the raw statement lol, my bad
"""


for root, dirs, files in os.walk("data"):
    for file in files:
        if file.endswith(".inc"):
            inc_path = os.path.join(root, file)
            pory_path = inc_path.replace(".inc", ".pory")
            with open(inc_path, 'r', encoding='utf-8') as inc_file:
                content = inc_file.read()
                if "DO NOT MODIFY" in content:
                    continue  # Skip if it contains the warning
                if content.replace(' ', '').replace('\n', '') == "":
                    continue  # Skip if content is empty or only whitespace
                if content.startswith("# 1 "):
                    continue  # Skip if already in pory format
            with open(pory_path, 'w', encoding='utf-8') as pory_file:
                pory_file.write(f"raw `\n{content}\n`\n")
            os.remove(inc_path)
