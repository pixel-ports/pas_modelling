import logging
import json
from typing import Iterable
import jsonschema

'''
1) INITIALISATION
- charger ce dont le module à besoin (ex: fichier de conf)
- vérifier que son input est conforme

2) PROCESSING
- transformer le PAS recu en appliquant les paramètres (ex: log étendus)

3) CLOSSING
- vérifier que son output est conforme
- renvoyer le PAS modifié
'''
def InputsCollector(call):
    #INITIALISATION
    settings = get_json("../"+"settings.json")

    #PROCESSING #TODO remplacer par la récupération sur l'IH (sur la base de call)
    Handlings, Rules, Supplychains, Resources = chargement_json(
        "."+settings_file["InputsCollector"]["inputs"]["path"],
        settings_file["InputsCollector"]["items"],
        settings_file["InputsCollector"]["inputs"]["suffix"],
    )
    #TODO empacter le résultat du process ?

    #CLOSSING
    for tuple_i in zip(
                [Handlings, Rules, Supplychains, Resources],
                chargement_json(
                    "."+settings["InputsCollector"]["schemas"]["path"],
                    settings["InputsCollector"]["items"],
                    settings["InputsCollector"]["schemas"]["suffix"],
                )
            ):
        jsonschema.validate(tuple_i[0], tuple_i[1])
    
    return data
#===================================================================

def chargement_json(folder_path: str, item_list: Iterable[str], suffix: str) :
    ''' 
    Charge des jsons du dossier donnée selon la séquence donnée en utilisant le suffix donné
    '''
    loaded_jsons = []

    for item in item_list :
        loaded_jsons.append(get_json(folder_path + item + suffix))
    return loaded_jsons
