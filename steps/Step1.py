import copy


class Step1:
    def __init__(self, pas):
        self.pas = pas

    def run(self):
        for ship in self.pas:
            for index, handling in enumerate(ship["HANDLINGS"]):
                handling["id"] = "%s-%s" % (ship["STOPOVER"]["ID"], index)
        # Use ETA_Dock on handling if available for priority definition, else use ETA_Port on ship
        self.pas.sort(
            key=lambda ship: min(
                [
                    handling["DOCK"]["ETA_dock"]
                    if handling["DOCK"]["ETA_dock"] is not None
                    else ship["STOPOVER"]["ETA_Port"]
                    for handling in ship["HANDLINGS"]
                ]
            )
        )
        return self.pas
