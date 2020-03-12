import logging
import json
from typing import Iterable
import jsonschema
from pathlib import Path

logger = logging.getLogger("IH_requeter")


def IH_requeter(PAS, module_settings, module_name):
    '''
    Converts IH request parameters to PAS modelling inputs (port's raw stopover and parameters set)
    '''

    # RÉCUPÉRATIONS STOPOVERS #FIXME remplacer par la récupération des données de l'IH (recus dans PAS["state"])
    PAS["state"] = [record["data"] for record in load(module_settings["handlings"]["full_path"])[0]["records"]] #Le 0 est pr le terminal de Bassens
    message = f"{module_name}: IH's stopover successfully imported" ; PAS["logs"]["run"].append(message) ; logger.warning(message)
    
    # RÉCUPÉRATION DES PARAMÈTRES #FIXME idem
    for parameter_name in module_settings["pas_parameters"]["name"] :
        PAS["parameters"][parameter_name] = load(
            module_settings["pas_parameters"]["folder_path"] + parameter_name + module_settings["pas_parameters"]["suffix"]
        )
        message = f"{module_name}: IH's parameter {parameter_name} successfully imported" ; PAS["logs"]["run"].append(message) ; logger.warning(message)
        # VÉRIFICATION DU JSON-SHEMA
        try:
            jsonschema.validate(
                PAS["parameters"][parameter_name], 
                load(
                    module_settings["schemas"]["folder_path"] + parameter_name + module_settings["schemas"]["suffix"]
                )
            )
            message = f"{module_name}: {parameter_name} successfully tested against shema" ; PAS["logs"]["run"].append(message) ; logger.warning(message)
        
        except: #FIXME catch le message d'erreur décrivant l'invalidité et le passer dans les logs
            PAS["log"]["module"].append(f"IH_requester: {parameter_name} unvalid against shema")
            message = f"{module_name}: {parameter_name} unvalid against shema" ; PAS["logs"]["run"].append(message) ; logger.warning(message)
            
        

    # logger.warning("Ending")
    return PAS

# %% UTILITIES
def load(full_path):
    assert Path(full_path).exists(), (
        f"ISSUE: {full_path} not found.\nCWD= {Path.cwd()}")
    with open(full_path) as file :
        return json.load(file)