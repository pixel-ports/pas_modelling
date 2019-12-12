class Step4:
    def __init__(self, pas, machines):
        self.pas = pas
        self.machines = machines

    def run(self):
        for stopover in self.pas:
            for handling in stopover["handlings"]:
                if handling["supplychain"] is not None:
                    for operation in handling["supplychain"][
                        "OPERATIONS_SEQUENCE"
                    ].values():
                        duration_hour = (
                            operation["endTS"] - operation["startTS"]
                        ) / 60.0
                        machine_consumption = self.machines[
                            operation["CALCULATION"]["Machine_ID"]
                        ]["SPECIFICATION"]["CONSUMPTION"]
                        assert (
                            len(machine_consumption["Electricity"].keys()) > 0
                        ), "Not yet implemented : An other energy type than electricity for machine"
                        operation["consumption"] = {
                            "electricityUnit": "kWh",
                            "electricity": machine_consumption["Electricity"][
                                "Power (kWh)"
                            ]
                            * duration_hour
                            if len(machine_consumption["Electricity"].keys()) > 0
                            else 0,
                        }
        return self.pas
