import copy


class Step1:
    """ Sort handlings
    """

    def __init__(self, pas):
        self.pas = pas

    def run(self):
        for stopover in self.pas:
            for index, handling in enumerate(stopover["handlings"]):
                handling["id"] = "%s-%s" % (stopover["stopover_ID"], index)
        # Use ETA_Dock on handling if available for priority definition, else use ETA_Port on ship
        self.pas.sort(
            key=lambda stopover: min(
                [
                    handling["dock"]["ETA"]
                    if handling["dock"]["ETA"] is not None
                    else stopover["port"]["ETA"]
                    for handling in stopover["handlings"]
                ]
            )
        )
        return self.pas
