import json
import jsonschema
import logging
import pandas as pd
#import dateutil.parser

# %% LOGGER
logging.basicConfig(
    level= logging.INFO, 
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")


def IH_converter(inputs, modSettings) :
    '''
    Transform previous PAS state into proper Handlings
    '''
    logger.warning("Begining IH_converter")

    # CHECK INPUT

    # PROCESSING
    output = {}
    output["parameters"] = inputs["parameters"]
    output["handlings"] = []
    
    for item in inputs["handlings"][0]["records"]:
        if item["data"].get("operation", None) == "unloading" : #FIXME c'est moche, on devrait pouvoir factoriser les champs communs
            output["handlings"].append(
                {
                    "boat_ID":str(item["data"].get("IMO", None)),
                    "boat_label": item["data"].get("name", None),
                    "ETArrival_dock": item["data"].get("arrival_dock", None), #FIXME on reste en epoch ==> ne respecte pas le json-schema
                    "ETDeparture_dock": item["data"].get("departure_dock", None), #FIXME idem
                    "stopover_ID":str(item["data"].get("journeyid", None)), 
                    "direction": item["data"].get("operation", None),
                    "agent": item["data"].get("unloading_agent", None),
                    "dock_ID":str(item["data"].get("unloading_berth", None)),
                    "segment": item["data"].get("unloading_cargo_fiscal_type", None),
                    "cargo": item["data"].get("unloading_cargo_type", None),
                    "dangerous": item["data"].get("unloading_dangerous", None),
                    "amount": item["data"].get("unloading_tonnage", None)
                }
            )
        elif item["data"].get("operation", None) == "loading" :
            output["handlings"].append(
                {   
                    "boat_ID":str(item["data"].get("IMO", None)),
                    "boat_label": item["data"].get("name", None),
                    "ETArrival_dock": item["data"].get("arrival_dock", None), #FIXME on reste en epoch ==> ne respecte pas le json-schema
                    "ETDeparture_dock": item["data"].get("departure_dock", None), #FIXME idem
                    "stopover_ID":str(item["data"].get("journeyid", None)), 
                    "direction": item["data"].get("operation", None),
                    "agent": item["data"].get("loading_agent", None),
                    "dock_ID":str(item["data"].get("loading_berth", None)),
                    "segment": item["data"].get("loading_cargo_fiscal_type", None),
                    "cargo": item["data"].get("loading_cargo_type", None),
                    "dangerous": item["data"].get("loading_dangerous", None),
                    "amount": item["data"].get("loading_tonnage", None),                    
            }
        ) #TODO filtrer les enregistrements dont un champ requi manque

    #juste pr check
    # with open("./export_IH_converter.json", "w") as file :
    #     json.dump(output, file)
    # FILTRATION

    # CHECK OUTPUT

    logger.warning("Ending IH_converter")
    return output


