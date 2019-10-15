import copy

class Step1:
    def __init__(self, pas_input):
        self.pas_input = pas_input


    def run(self):

        ## Sort handlings
        handlings = []
        for ship in self.pas_input:
            for index, handling in enumerate(ship["HANDLINGS"]):
                handling["STOPOVER_ETA_Port"] = ship["STOPOVER"]["ETA_Port"]
                handling["processed"] = {
                    "shipId": ship["STOPOVER"]["ID"],
                    "indexInShip": index
                }
                handling["id"] = "%s-%s" % (handling["processed"]["shipId"], handling["processed"]["indexInShip"])
                handlings.append(copy.deepcopy(handling))
        handlings = [handling for handling in handlings if handling["CARGO"] is not None]
        handlings.sort(key=lambda h: (h["STOPOVER_ETA_Port"], h["DOCK"]["ETA_dock"]))
        for handling in handlings:
            del handling["STOPOVER_ETA_Port"]

        return handlings
