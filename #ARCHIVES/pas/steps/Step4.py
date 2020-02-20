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
                            for resource in activity["resources_accounts_list"]:
                                machine = next(
                                    machine
                                    for machine in self.resources["machines"]
                                    if machine["ID"] == resource["resource_ID"]
                                )
                                energy_consumed = []
                                for consumption in machine["consumptions"]:
                                    energy_consumed.append(
                                        {
                                            "nature": consumption["nature"],
                                            "value": consumption["value"]
                                            * activity["timespan_scheduled"]["duration"]
                                            / 60,
                                        }
                                    )
                                resource["energy_consumed"] = energy_consumed
        return self.pas
