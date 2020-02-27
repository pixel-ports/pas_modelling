import itertools 
print("\n\n\n")


#%% TEST MODIF CONSTANTE
'''
CONSTANTE = {
    "foo":"bar"
}

def modif(dict_passed):
    dict_passed["new key"] = "toto"
    dict_passed["foo"] = "bar-bq"
    return dict_passed

print(modif(CONSTANTE))
'''

#%% TEST ITER VIDE
'''
liste = []

for item in liste :
    print(item)

print([len(item) for item in liste])
'''

# %% DATA

handling_list = [
    {
        "contType": "contType_2",
        "critere": "foo",
        "supChain_list":[]
    }
]

contType_list = [
    {
        "contType_ID": "contType_1",
        "possibles_supChain": [] #Tester variante {ss clé, None}
    },
    {
        "contType_ID": "contType_2",
        "possibles_supChain": [
            {
                "supChain_ID": "supChain_1", 
                "critere": "foo"
            }, 
            {
                "supChain_ID": "supChain_2", 
                "critere": "foo"
            }
        ]
    },
    {
        "contType_ID": "contType_2",
        "possibles_supChain": [
            {
                "supChain_ID": "supChain_3", #Tester nom en doublon
                "critere": "foo"
            },
            {
                "supChain_ID": "supChain_4", 
                "critere": "bar"
            }
        ]    
    }
]


# %% Approche boucles
temp_list = []
for handling in handling_list :

    for contType in contType_list :
        if contType["contType_ID"] == handling["contType"] :
            for supChain in contType["possibles_supChain"] :
                temp_list.append(supChain)
                #---------------------------------------------
                if supChain["critere"] == handling["critere"] :
                    handling["supChain_list"].append(supChain["supChain_ID"])
    print(f'Boucle: {temp_list}')
    handling["supChain_list"] = set(handling["supChain_list"])
    # print(f'result_BOUCLE: {handling["supChain_list"]}')
#Fonctionne, mais ne permet pas d'envoyer les logs de handlings sans matching ct ni sans matching supChain

# %% Approche list comprehension
# On cherche à recréer temp_list en list comprehension
for handling in handling_list :
    candidatSC_list = [
        supChain for supChain 
        in contType["possibles_supChain"]
        for contType in contType_list
        if contType["contType_ID"] == handling["contType"]
    ]
    print(f'Liste  : {candidatSC_list}')
# %%

print(f'Identiques: {temp_list == candidatSC_list} FIN')