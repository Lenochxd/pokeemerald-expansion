import json

f = open("pokedex.json", "r", encoding="utf-8")
data = json.load(f)
f.close()

remove = ['type', 
          'base',
          'species', 
          'evolution',
          'profile', 
          'image']

for i in range(len(data)):
    for key in remove:
        if key in data[i]:
            del data[i][key]
    
f = open("pokedex_clean.json", "w", encoding="utf-8")
json.dump(data, f, ensure_ascii=False, indent=4)
f.close()