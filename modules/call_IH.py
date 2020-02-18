import logging
import json
from typing import Iterable
import jsonschema

# %% LOGGER
logging.basicConfig(
    level= logging.INFO, 
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")

'''
Appelle l'IH sur la base des données passées, pour récupérer toutes les informations (input=handling + paramètres=set_parameters), les mettres dans un object unique renvoyé
'''
def call_IH(inputs, modSettings):

    logger.warning("Begining call_IH")

    # %% CHECKING INPUTS
    #TODO passer par un shema sur le call ? 

    #PROCESSING #TODO remplacer par la récupération sur l'IH (sur la base de input)
    output = {}

    ##HANDLINGS
    output["handlings"] = load(modSettings["handlings"]["full_path"])

    ##SET_PARAMETERS
    output["parameters"] = {}
    for item in modSettings["set_parameters"]["name"] :#TODO assert etc
        output["parameters"][item] = load(
            modSettings["set_parameters"]["folder_path"] +
            item +
            modSettings["set_parameters"]["suffix"]
            )

    #CHECKING output
    for item in modSettings["set_parameters"]["name"] :
        jsonschema.validate(
            output["parameters"][item], 
            load(
                #"." +
                modSettings["schemas"]["folder_path"] +
                item +
                modSettings["schemas"]["suffix"]
            )
        )

    logger.warning("Ending call_IH")
    return output 

# %% UTILITIES
def load(full_path):
    with open(full_path) as file :
        return json.load(file)