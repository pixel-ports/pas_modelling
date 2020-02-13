import logging
import jsonschema

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")


class Step0:
    """ Act as a surrogate for the converter (filtering some handling, correct some content>nature values, checking against schema...), 
    """
    #TODO Transférer les règles dans un json de conf

    def __init__(self, pas):
        self.pas = pas

    def run(self):
        
        handlings = chargement_PAS(pas)
        
        
        
        #logger.warning("Toto!!!")

        return self.pas

    def chargement_PAS (PAS)
        handlings = [
            handling
            for terminal in self.pas
            for ship in terminal["ships_list"]
            for stopover in ship["stopovers_list"]
            for handling in stopover["handlings_list"]
        ]

        return handlings