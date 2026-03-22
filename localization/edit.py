"""edit the pokedex.json file to be more easily used in the localization process"""

import json

f = open("pokedex.json", "r", encoding="utf-8")
data = json.load(f)
f.close()

updated = {}

for i in range(len(data)):
    updated[str(data[i]['id'])] = data[i]
    updated[str(data[i]['id'])].pop('id')
    
f = open("pokedex_clean.json", "w", encoding="utf-8")
json.dump(updated, f, ensure_ascii=False, indent=4)
f.close()