import logging
import json
from typing import Iterable
import jsonschema
from pathlib import Path

logger = logging.getLogger("IH_requester")
mod_name = "IH_requester:"

def IH_requester(HANDLINGS, PARAMETERS, MODLOGS, MODSETTINGS):
    '''
    Converts IH request parameters to PAS modelling inputs (port's raw stopover and parameters set)
    '''

    # RÉCUPÉRATIONS STOPOVERS #FIXME remplacer par la récupération des données de l'IH (recus dans PAS["HANDLINGS"])
    HANDLINGS = <<mettre fonction pr get data [record["data"] for record in load(MODSETTINGS["handlings"]["full_path"], MODLOGS)[0]["records"]] #Le 0 est pr le terminal de Bassens
    MODLOGS.append(f"{mod_name} IH's stopover successfully imported")
    

    # RÉCUPÉRATION DES PARAMÈTRES 
    # for parameter_name in MODSETTINGS["pas_parameters"]["name"] :
    #     # CHARGEMENT DU JSON #FIXME idem
    #     PARAMETERS[parameter_name] = load(
    #         MODSETTINGS["pas_parameters"]["folder_path"] + parameter_name + MODSETTINGS["pas_parameters"]["suffix"],
    #         MODLOGS
    #     )
    #     message = f"IH_requester: IH's parameter {parameter_name} successfully imported" ; MODLOGS.append(message) ; logger.warning(message)
        
    #     # CHARGEMENT DU SCHEMA
    #     schema_path = "toto" + MODSETTINGS["schemas"]["folder_path"] + parameter_name + MODSETTINGS["schemas"]["suffix"]
    #     try :
    #         with open(schema_path) as file :
    #             schema = json.load(file)
    #     except FileNotFoundError: 
    #         message = f"IH_requester: json-schema parameter {parameter_name} file not found in {schema_path}" ; MODLOGS.append(message) ; logger.warning(message)
    #     except ValueError: 
    #         message = f"IH_requester: json-schema parameter {parameter_name} can not be loaded (invalid json)" ; MODLOGS.append(message) ; logger.warning(message)
    #     else:
    #         message = f"IH_requester: json-schema parameter {parameter_name} succefully loaded" ; MODLOGS.append(message) ; logger.warning(message)    
        
    #     # CONFRONTATION JSON VS SCHEMA
    #     try:
    #         jsonschema.validate(
    #             PAS["parameters"][parameter_name], 
    #             schema
    #         )       
    #     except: #FIXME catch le message d'erreur décrivant l'invalidité et le passer dans les MODLOGS
    #         MODLOGS.append(f"IH_requester: {parameter_name} unvalid against shema")
    #         message = f"IH_requester: {parameter_name} unvalid against shema" ; MODLOGS.append(message) ; logger.warning(message)
    #     else :
    #         message = f"IH_requester: {parameter_name} successfully tested against shema" ; MODLOGS.append(message) ; logger.warning(message)
    
        

    # logger.warning("Ending")
    return (HANDLINGS, PARAMETERS, MODLOGS, MODSETTINGS)

# %% UTILITIES
def load(file_path):
    try :
        with open(file_path) as file :
            loaded_json = json.load(file)
    except FileNotFoundError: 
        message = f"IH_requester: {file_path} file not found"
    except ValueError: 
        message = f"IH_requester: {file_path} can not be loaded (invalid json)"
    else:
        message = f"IH_requester: {file_path} succefully loaded"
        return loaded_json, message