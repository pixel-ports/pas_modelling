import json
import jsonschema
import logging
import strict-rfc3339

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
    output["handlings"] = []
    
    for item in inputs["handlings"][0]["records"]:
        output["handlings"].append(#).update(
            {
                "departure_dock": item["data"].get("departure_dock", None),
                "boat_ID":str(
                    item["data"].get("IMO", None)
                    ), 
                
                "ETArrival_dock": datetime.datetime(item["data"].get("arrival_dock", None)).isoformat("T")
                # datetime.datetime.strptime(
                #     , 
                #     "%Y-%m-%dT%H:%M:%S.%fZ"
                #     ).isoformat()
                    
                # "ETDeparture_dock": 1515359700000,
                # "boat_ID": 9571545,
                # "journeyid": 20180001,
                # "name": "MUNTGRACHT",
                # "operation": "unloading",           
            }
        )


    # CONVERSIONS

    logger.warning("Ending IH_converter")
    return output


