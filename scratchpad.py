#%%
liste = [1, 2, 3, 2]

target = 2

# %%
for item in liste:
    if item == target:
        print("target aquired")

# %%
for item in iter(item == iter(liste)):
     print("target aquired")

# %%
dic = {
    "Asignations": [
        {
            "CT": 2,
            "Suitable_SCs": [
                {
                    "SC": "sc_1",
                    "requirements":"riri"
                },
                {
                    "SC": "sc_2",
                    "requirements":"fifi"
                }
            ]
        },
        {
            "CT": 2,
            "Suitable_SCs": [
                {
                    "SC": "sc_3",
                    "requirements":"riri"
                },
                # {
                #     "SC": "sc_4",
                #     "requirements":"loulou"
                # }
            ]
        },
        {
            "CT": 3,
            "Suitable_SCs": [
            ]
        },
        {
            "CT": 4
        }
    ]
}

result = [asignation.get("Suitable_SCs", []) 
    for asignation in dic["Asignations"] 
    if asignation["CT"] == 2
]

print(f"nb de CT qui matchent: {len(result)}")

result

flat_result = [sc for ct in result for sc in ct]

flat_result

# %%
[asignation.get("Suitable_SCs", []) 
    for asignation in dic["Asignations"]
    for item in asignation
    if asignation["CT"] == 2
    
]

# %%
result = []
for asignation in dic["Asignations"] :
    for sc in asignation.get("Suitable_SCs", []) :
        if asignation["CT"] == 2 :
            result.append(sc)

print(result)

# %%
[sc 
    for asignation in dic["Asignations"]
    for sc in asignation.get("Suitable_SCs", [])
    if asignation["CT"] == 3
]
# %%
toto = {"une clé": "une valeur"}
toto.setdefault("setdefault",[]).append("ajout 1")
toto.setdefault("setdefault",2).append("ajout 1.2")
print(toto)
toto.get("get",[]).append("ajout 2")
print(toto)
toto.get("get",[]).append("ajout 3")
print(toto)
# %%
liste.append(None)

# %%
liste

# %%
