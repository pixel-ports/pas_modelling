import copy


class Step1:
    """ Sort handlings
    """

    def __init__(self, pas):
        self.pas = pas

    def run(self):
        handlings = [handling for terminal in self.pas for ship in terminal["ships_list"] for stopover in ship["stopovers_list"] for handling in stopover["handlings_list"]]
        handlings.sort(
            key=lambda handling: handling["dock"]["ETA"]
        )
        for index, handling in enumerate(handlings):
            handling["number_in_queue"] = index
        return self.pas
