import logging
import json
from typing import Iterable
import jsonschema
from pathlib import Path

# %% LOGGER
logger = logging.getLogger("IH_getter")

'''
Appelle l'IH sur la base des données passées, pour récupérer toutes les informations (input=handling + paramètres=set_parameters), les mettres dans un object unique renvoyé
'''
def IH_getter(IH_call_parameters, modSettings):

    logger.warning("Starting")

    # %% CHECKING INPUTS
    #TODO passer par un shema sur le call ? 

    #PROCESSING #TODO remplacer par la récupération sur l'IH (sur la base de input)
    pas = {}

    ##HANDLINGS
    pas["handlings"] = load(
        modSettings["handlings"]["full_path"])

    ##SET_PARAMETERS
    pas["parameters"] = {}
    for item in modSettings["set_parameters"]["name"] :#TODO assert etc
        #logger.warning(f"loading : {file_path}")
        pas["parameters"][item] = load(
            modSettings["set_parameters"]["folder_path"] +
            item +
            modSettings["set_parameters"]["suffix"]
        )
    #CHECKING OUTPUT
    #FIXME compléter le set de json-schema et réactiver cette partie
    # for item in modSettings["set_parameters"]["name"] :
    #     jsonschema.validate(
    #         pas["parameters"][item], 
    #         load(
    #             #"." +
    #             modSettings["schemas"]["folder_path"] +
    #             item +
    #             modSettings["schemas"]["suffix"]
    #         )
    #     )

    logger.warning("Ending")
    return pas 

# %% UTILITIES
def load(full_path):
    assert Path(full_path).exists(), (
        f"ISSUE: {full_path} not found.\nCWD= {Path.cwd()}")
    with open(full_path) as file :
        return json.load(file)