print("\n\n\n")

# %% DATA

handling = {
    "contentType": "contentType_2",
    "critere": "foo",
    "supplychain_list":[]
}

contentType_list = [
    {
        "contentType_ID": "contentType_1",
        "possibles_supplychain": [] #Tester variante {ss clé, None}
    },
    {
        "contentType_ID": "contentType_2",
        "possibles_supplychain": [
            {
                "supplychain_ID": "CT2_SC_1", 
                "critere": "foo"
            }, 
            {
                "supplychain_ID": "CT2_SC_2", 
                "critere": "foo"
            }
        ]
    },
    {
        "contentType_ID": "contentType_2",
        "possibles_supplychain": [
            {
                "supplychain_ID": "CT2doublon_SC_1", #Tester nom en doublon
                "critere": "foo"
            },
            {
                "supplychain_ID": "CT2doublon_SC_2", 
                "critere": "bar"
            }
        ]    
    }
]


# %% Approche boucles

handling["supplychain_list"]=[]
temp_list = []
for contentType in contentType_list :
    if contentType["contentType_ID"] == handling["contentType"] :
        for supplychain in contentType["possibles_supplychain"] :
            if supplychain["critere"] == handling["critere"] :
                handling["supplychain_list"].append(supplychain["supplychain_ID"])

handling["supplychain_list"] = set(handling["supplychain_list"])

print(f'result_BOUCLE: {handling["supplychain_list"]}')
#Fonctionne, mais ne permet pas d'envoyer les logs de handlings sans matching ct ni sans matching supplychain

#%% New list comp

handling["supplychain_list"] = set([
    supplychain["supplychain_ID"]
    for contentType in contentType_list if contentType["contentType_ID"] == handling["contentType"]
    for supplychain in contentType["possibles_supplychain"] if supplychain["critere"] == handling["critere"]
])

print(f'result_NEWLISTE: {handling["supplychain_list"]}')

# %% REFONTE ASSIGNATION

#%% Nouveau parametre
'''
 #Renommer l'entite de parametres content_types en assignations?
Par quel bout le prendre ? nature(interne system)>X(pas toujours présent)>contentType(toujours présent)
 #utiliser champs fixes pr illustrer que paramètre interne ? ou filister les HT compatibles sur une base de paramètres ? <-- Non ne pas penser fichier settings, mais json Dashboard
'''
'''
handling = {
    #<<"handlingType": "cereal", #la clé handlingType devient ce qui était avant "nature" (cargo, paquebot, porte conteners). Elle est déduite à la convertion en parcourant l'arbre CONTENT
    "contentSegment": "cereal", #à présent
    "contentType": "blé",
    "critere": "foo",
    "supplychain_list":[]
}
CONTENTS = {#on peut passer en array pr parcourir les nature, ou iterer sur CONTENT.key()
    "cargo": [
        {
            "contentType_ID":"cereal",#On pourrait vouloir virer ce niveau, mais alors plus de SC par défault !
            "contentType_list": [
                {
                    "contentType_ID": "maïs",
                    "possibles_supplychain": [] #Tester variante {ss clé, None}
                },
                {
                    "contentType_ID": "blé",
                    "comment": "l'original normal",
                    "possibles_supplychain": [
                        {
                            "supplychain_ID": "blé_SC_1", 
                            "critere": "foo"
                        }, 
                        {
                            "supplychain_ID": "blé_SC_2", 
                            "critere": "foo"
                        }
                    ]
                },
                {
                    "contentType_ID": "blé",
                    "comment": "le doublon de test",
                    "possibles_supplychain": [
                        {
                            "supplychain_ID": "blé_SC_1", 
                            "critere": "foo"
                        }, 
                        {
                            "supplychain_ID": "bléDoublon_SC_2nomDifferent", 
                            "critere": "foo"
                        }
                    ]
                },
                {
                    "contentType_ID": "tournesol",
                    "possibles_supplychain": [
                        {
                            "supplychain_ID": "tournesol_SC_1", #Tester nom en doublon
                            "critere": "foo"
                        },
                        {
                            "supplychain_ID": "tournesol_SC_2", 
                            "critere": "bar"
                        }
                    ]    
                }
            ]
        }
    ],
    "paquebot": [
        {
            "handlingType": "paquebot",
            "contentType_list":[
                {
                    "contentType_ID": "passengers",
                    "possibles_supplychain": [] #Tester variante {ss clé, None}
                }
            ]
        }
    ]
}


#%%
handling["supplychain_list"] = set([supplychain["supplychain_ID"]
    CONTENTS.keys()
    for handlingType in  if handlingType["handlingType_ID"] == handling["handlingType"] #Lorsque on doit avoir un éléments en dur, on convertie la valeur en clée parente
    for contentType in handlingType["contentType_list"] if contentType["contentType_ID"] == handling["contentType"]
    for supplychain in contentType["possibles_supplychain"] if supplychain["critere"] == handling["critere"] #test_SCrestriction(handling, supplychain, settings)
]) #FIXME Non! l'assignation d'une SC par ce processus n'est pas limité au cargo. Du coup modifier pr rajouter une étape pr parcourir les natures

if len(handling["supplychain_list"]) == 0 : # and setting["activate _assign_defaultSC"]
    print('assign_defaultSC(handling, HANDLING_MAPPING, settings)')

print(f'result_REFONTE: {handling["supplychain_list"]}')


# %%
for handlingType in CONTENTS.keys():
    print(handlingType)
'''
#==========================================================================

# %%
handling = {
    #<<"handlingType": "cereal", #la clé handlingType devient ce qui était avant "nature" (cargo, paquebot, porte conteners). Elle est déduite à la convertion en parcourant l'arbre CONTENT
    "contentSegment": "cereal", #à présent
    "handlingType": "cereal",
    "contentType": "blé",
    "critere": "foo",
    "supplychain_list":[]
}
CONTENTS = { #Par convention, un data-model doit être un object, pas un array
    "cargo": [ #Par convension, les "paramètres" fixés en dur doivent être sous forme de clée, pas de valeurs
        {
            "contentSegment_ID":"cereal",#Optionel (on peut mettre tous les contenType sous un même Segment), permet des aggrégations et l'assignation de SC par défaut
            "contentType_list": [
                {
                    "contentType_ID": "maïs",
                    "possibles_supplychain": [] #Tester variante {ss clé, None}
                },
                {
                    "contentType_ID": "blé",
                    "comment": "l'original normal",
                    "possibles_supplychain": [
                        {
                            "supplychain_ID": "blé_SC_1", 
                            "critere": "foo"
                        }, 
                        {
                            "supplychain_ID": "blé_SC_2", 
                            "critere": "foo"
                        }
                    ]
                },
                {
                    "contentType_ID": "blé",
                    "comment": "le doublon de test",
                    "possibles_supplychain": [
                        {
                            "supplychain_ID": "blé_SC_1", 
                            "critere": "foo"
                        }, 
                        {
                            "supplychain_ID": "bléDoublon_SC_2nomDifferent", 
                            "critere": "foo"
                        }
                    ]
                },
                {
                    "contentType_ID": "tournesol",
                    "possibles_supplychain": [
                        {
                            "supplychain_ID": "tournesol_SC_1", #Tester nom en doublon
                            "critere": "foo"
                        },
                        {
                            "supplychain_ID": "tournesol_SC_2", 
                            "critere": "bar"
                        }
                    ]    
                }
            ]
        },
        {
            "contentSegment_ID":"hydrocarbures",#On pourrait vouloir virer ce niveau, mais alors plus de SC par défault !
            "contentType_list": [
                {
                    "contentType_ID": "pétrol",
                    "possibles_supplychain": [] #Tester variante {ss clé, None}
                }
            ]
        }
    ],
    "paquebot": [
        {
            "contentSegment_ID": "paquebot",
            "contentType_list":[
                {
                    "contentType_ID": "passengers",
                    "possibles_supplychain": [] #Tester variante {ss clé, None}
                }
            ]
        }
    ]
}
#%%
'''
CONTENTS.values(): [
    "handlingType_list": [
        {
            contentSegment_ID
            contentType_list: [
                {
                    contentType_ID
                    possibles_supplychain:[
                        {
                            supplychain_ID
                            assignation_restriction:[]
'''

handling["supplychain_list"] = set([supplychain["supplychain_ID"]
    for handlingType_list in CONTENTS.values() #hérité de le contrainte de convention 1
    for contentSegment in handlingType_list if contentSegment["contentSegment_ID"] == handling["contentSegment"] #Elaguage optionnel de l'arbre à parcourir
    for contentType in contentSegment["contentType_list"] if contentType["contentType_ID"] == handling["contentType"]
    for supplychain in contentType["possibles_supplychain"] if supplychain["critere"] == handling["critere"] #test_SCrestriction(handling, supplychain, settings)
])

if len(handling["supplychain_list"]) == 0 : # and setting["activate _assign_defaultSC"]
    print('assign_defaultSC(handling, HANDLING_MAPPING, settings)')

print(f'result_REFONTE: {handling["supplychain_list"]}')

print("END3")
