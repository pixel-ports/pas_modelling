import copy


class Step1:
    def __init__(self, pas_input):
        self.pas_input = pas_input

    def run(self):
        for ship in self.pas_input:
            for index, handling in enumerate(ship["HANDLINGS"]):
                handling["id"] = "%s-%s" % (ship["STOPOVER"]["ID"], index)
        # Use ETA_Dock on handling if available for priority definition, else use ETA_Port on ship
        self.pas_input.sort(
            key=lambda ship: min(
                [
                    handling["DOCK"]["ETA_dock"]
                    if handling["DOCK"]["ETA_dock"] is not None
                    else ship["STOPOVER"]["ETA_Port"]
                    for handling in ship["HANDLINGS"]
                ]
            )
        )
        return self.pas_input
