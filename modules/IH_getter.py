import logging
import json
from typing import Iterable
import jsonschema
from pathlib import Path

logger = logging.getLogger("IH_getter")


def IH_getter(pas, module_settings):
    '''
    Converts call_parameters to stopover_seed (raw data from IH)
    '''
    logger.warning("Starting")

    # %% CHECKING INPUTS
    #TODO passer par un shema sur le call ? 

    #PROCESSING 
    ## Récupérations stopovers #TODO remplacer par la récupération sur l'IH (sur la base de call_parameters)
    pas["state"] = [record["data"] for record in load(module_settings["handlings"]["full_path"])[0]["records"]] #Le 0 est pr le terminal de Bassens
    #LOG
    
    ## Récupération des paramètres
    for parameter_name in module_settings["pas_parameters"]["name"] :
        pas["parameters"][parameter_name] = load(
            module_settings["pas_parameters"]["folder_path"] +
            parameter_name +
            module_settings["pas_parameters"]["suffix"]
        )

        ## Vérification du json-shema
        try:
            jsonschema.validate(
                pas["parameters"][parameter_name], 
                load(
                    #"." +
                    module_settings["schemas"]["folder_path"] +
                    parameter_name +
                    module_settings["schemas"]["suffix"]
                )
            )
        except: #FIXME Erreur chagement ou validation
            pass
        #LOG
        

    logger.warning("Ending")
    return pas

# %% UTILITIES
def load(full_path):
    assert Path(full_path).exists(), (
        f"ISSUE: {full_path} not found.\nCWD= {Path.cwd()}")
    with open(full_path) as file :
        return json.load(file)