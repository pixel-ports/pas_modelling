import json
import jsonschema
import logging

#logging.basicConfig(level=logging.INFO, format='%(name)-8s %(message)s')
logger = logging.getLogger("SC_mapper")

def SC_mapper(inputs, modSettings) :
    '''
    Transform previous PAS state into proper Handlings
    Options:
    - enable restriction filtering (default: False)
    - allow multiple SC (default: False)
    '''
    logger.warning("Starting")
    for handling in inputs["handlings"] :
        pass 
    logger.warning("Ending")
    return inputs


