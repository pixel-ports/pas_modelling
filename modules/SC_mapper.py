import json
import jsonschema
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")

def SC_mapper(INPUT, modSettings) :
    '''
    Transform previous PAS state into proper Handlings
    '''
    logger.warning("Begining SC_mapper")
    
    logger.warning("Ending SC_mapper")
    return PAS


