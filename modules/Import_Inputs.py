# CHARGEMENT
import logging
import json
from typing import Iterable
import jsonschema

class Import_Inputs :
    '''
    Transform previous PAS state into proper Handlings
    '''
    def __init__(self, PAS):
        self.PAS = PAS

    def checkIn(self):
        logger.warning("Begining Handlings checkIn") 
        # CHARGEMENT INPUTS

        #Settings
        with open("./settings.json") as file :
            settings = json.load(file)

        logger.warning("Finishing Handlings checkIn") 
        return True
    
    def process(self):
        logger.warning("Begining Handlings processing") 
        #TODO 
        logger.warning("Finishing Handlings processing") 
        return 

    def checkOut(self):
        logger.warning("Begining Handlings checkOut") 
        #TODO un try ou direct un jsonshema.validate()
        logger.warning("Finishing Handlings checkOut") 
        return 
    
def chargement_json(folder_path: str, item_list: Iterable[str], suffix: str) :
    ''' 
    Charge des jsons du dossier donnée selon la séquence donnée en utilisant le suffix donné
    '''
    #TODO convertir en un truc propre 

    loaded_jsons = []

    for item in item_list :
        with open(folder_path + item + suffix) as json_file:
            item = json.load(json_file)
        loaded_jsons.append(item)

    return loaded_jsons

def schema_checking(tuples_list: Iterable[tuple]) :
    '''
    Confronte les json à leurs schema. On fournit une liste de tuples sous la forme (json, schema)
    '''
    #TODO ne pas se contenter de faire crasher le bousin

    for item in tuples_list :
        jsonschema.validate(item[0], item[1])

# RUN

## INITIALISATION
item_list = [
        "CARGOES_HANDLING_REQUESTS", 
        "RULES", 
        "SUPPLYCHAINS", 
        "RESOURCES", 
        ]

#Chargement des inputs
handlings, rules, supplychains, resources = chargement_json(
    folder_path= "./inputs/simple_examples/",
    item_list= item_list,
    suffix= ".json"
)

#Chargement des schémas
handlings_schema, rules_schema, supplychains_schema, resources_schema = chargement_json(
    folder_path= "./tools/json_schema/",
    item_list= item_list,
    suffix= "_schema.json"
)

#Test de validités des schémas
schema_checking(zip(
    [handlings, rules, supplychains, resources],
    [handlings_schema, rules_schema, supplychains_schema, resources_schema]
    )
)

#ORDONNANCEMENT
#TODO en respectant la conf donnée par Rules

print("\n\n\n GREEAT !!! \n\n\n")