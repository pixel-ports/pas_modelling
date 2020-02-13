import copy
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")

class Step2:
    """ Affect a supplychain to each handling
    """

    def __init__(self, pas, rules, supplychains):
        self.pas = pas
        self.rules = rules
        self.supplychains = supplychains

    def __set_ids_for_steps(self):
        for supplychain in self.supplychains:
            for step in supplychain["steps_list"]:
                step["full_id"] = "%s-%s" % (
                    supplychain["ID"],
                    step["ID"],
                )  # For later use in Step3

    def __get_sorted_handlings(self):
        """
        Precondition : handlings have been sorted in Step1 earlier
        """
        #TODO comprendre prk on réapplique un tri
        handlings = [
            handling
            for terminal in self.pas
            for ship in terminal["ships_list"]
            for stopover in ship["stopovers_list"]
            for handling in stopover["handlings_list"]
        ]
        handlings.sort(key=lambda handling: handling["ID"])
        return handlings

    def run(self):
        self.__set_ids_for_steps()
        for handling in self.__get_sorted_handlings():
            assert (
                handling["nature"] == "cargo"
            ), "Handling types other than 'cargo' are not yet implemented"
            selected_supplychain = self.select_supplychain(handling)
            if selected_supplychain is None:
                handling["supply_chain_ID"] = None
            else:
                handling["supply_chain_ID"] = selected_supplychain["ID"]
        return self.pas

    def select_supplychain(self, handling):
        filtered_supplychains = [
            sc for sc in self.supplychains if self.is_matching(handling, sc)
        ]
        if len(filtered_supplychains) == 1:
            selected_supplychain = filtered_supplychains[0]
        else:
            logger.warning(
                f"(Step2) Supplychain attribution issue: There should be one, and only one, matching supplychain but there are {len(filtered_supplychains)} matchs for handling {json.dumps(handling)}"
                #ajouter de l'info : es que le content>category match Rules>
            )
            selected_supplychain = None  #  Default if no supplychain is matched
        return selected_supplychain

    def is_matching(self, handling, supplychain):
        # filetered_supplychains_ids = [
        #     assignation["supply_chain_ID"]
        #     for category in self.rules["cargoes_categories"]
        #     if category["ID"] == handling["contents"]["category"]
        #     for assignation in category["assignation_preference"]
        # ]  # TODO : There may be 0 OR multiple assignations to choose from

        filetered_supplychains_ids = []

        for category in self.rules["cargoes_categories"] :
            
            nbMatch_CC = 0 
            nbMatch_dock = 0 #Compteur pr vérifier cohérence et informer user
            if category["ID"] == handling["contents"]["category"] :
                
                nbMatch_CC += 1
                for assignation in category["assignation_preference"] :
                    if handling["dock"]["ID"] in assignation["dock_ID"] : #Ajout de la prise en compte du dock
                        nbMatch_dock += 1
                        filetered_supplychains_ids.append(assignation["supply_chain_ID"])

            if len(filetered_supplychains_ids) == 0 :
                assert (nbMatch_dock == 0), f"Incoherent behavior, if filetered_supplychains_ids ==0, nbMatch_dock should also ==0 (but equal {nbMatch_dock})" #Un peu verbeux ? On peut supprimer
                logger.warning(
                    f"(Step2) Rules application issue: no matching cargo category (theire is {nbMatch_CC} matching CC but {nbMatch_dock} compatible with handling dock) for {json.dumps(handling)}" 
                )

        return supplychain["ID"] in filetered_supplychains_ids