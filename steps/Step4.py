class Step4:
    def __init__(self, pas, resources):
        self.pas = pas
        self.resources = resources

    def run(self):
        for terminal in self.pas:
            for ship in terminal["ships_list"]:
                for stopover in ship["stopovers_list"]:
                    for handling in stopover["handlings_list"]:
                        for activity in handling["activities_list"]:
                            for ressource in activity["ressources_accounts_list"]:
                                machine = next(machine for machine in self.resources["machines"] if machine["ID"]==ressource["ressource_ID"])
                                energy_consumed = []
                                for consumption in machine["consumptions"]:
                                    assert consumption["nature"] == "electricity", "At this time, only the electricity consumption has been implemented, but found consumption nature to be %s" % consumption["nature"]
                                    assert consumption["unit"]=="kWh", "Unknown consumption unit : %s" % consumption["unit"]
                                    energy_consumed.append({
                                        "nature": consumption["nature"],
                                        "unit": "kW",
                                        "value": consumption["value"] * activity["timespan_scheduled"]["duration"]/60
                                    })
                                ressource["energy_consumed"] = energy_consumed
        return self.pas
