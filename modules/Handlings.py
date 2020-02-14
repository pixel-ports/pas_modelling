import json
import jsonschema
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")

class Handlings :
    '''
    Transform previous PAS state into proper Handlings
    '''
    def __init__(self, PAS):
        self.PAS = PAS

    def checkIn(self):
        logger.warning("Begining Handlings checkIn") 
        # CHARGEMENT INPUTS

        #Settings


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


