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
def InputsCollector(call, settings_i):

    #CHECKING INPUTS
    #TODO passer par un shema sur le call ? 
   
    #PROCESSING #TODO remplacer par la récupération sur l'IH (sur la base de call)
    #TODO Séparer récupération CHR et settings

    loaded_jsons = []
    for item in settings_i["items"] :#TODO assert etc
        loaded_jsons.append(load(settings_i["inputs"]["path"] + item + ".json")) 
    Handlings, Rules, Supplychains, Resources = iter(loaded_jsons) #TODO avoir ça en dur !?!

    #CHECKING OUTPUT
    for tuple_i in zip(
                [Handlings, Rules, Supplychains, Resources],
                chargement_json(
                    "."+settings["InputsCollector"]["schemas"]["path"],
                    settings["InputsCollector"]["items"],
                    settings["InputsCollector"]["schemas"]["suffix"],
                )
            ):
        jsonschema.validate(tuple_i[0], tuple_i[1])
    
    return handlings
