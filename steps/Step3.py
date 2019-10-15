import copy
import numpy as np

class Step3:

    def __init__(self, activities, machines):
        self.activities = activities
        self.machines = machines
        self.uses = []

    def run(self):
        for id, machine in self.machines.items():
            machine["id"] = id
        for activity in self.activities:
            handling = activity["pair"]["handling"]
            dockingTS = handling["DOCK"]["ETA_dock"]
            supplychain = activity["pair"]["supplychain"]
            operations = copy.deepcopy(supplychain["OPERATIONS_SEQUENCE"])
            ids_to_process = list(operations.keys())
            ids_processed = []
            while len(ids_to_process) > 0:
                for id in ids_to_process:
                    operation = supplychain["OPERATIONS_SEQUENCE"][id]
                    machine = self.machines[operation["CALCULATION"]["Machine_ID"]]
                    operation_processed = False

                    if operation["CALCULATION"]["Start_Type"] == "ASAP":
                        startingTS = dockingTS
                        operation_processed = True
                    elif isinstance(operation["CALCULATION"]["Start_Type"], dict):
                        assert "Case_0" in operation["CALCULATION"]["Start_Type"].keys(), "Problem with StartType keys"
                        conditions = operation["CALCULATION"]["Start_Type"]["Case_0"]
                        assert np.all([list(condition.keys())[0] in ["After", "With"] for condition in conditions]), "Not yet implemented : other keys than After/With"
                        conditions_ids = [list(condition.values())[0] for condition in conditions]
                        if np.all([id in ids_processed for id in conditions_ids]):
                            candidates_startingTS = []
                            for condition in conditions:
                                assert len(condition.keys()) == 1, "There can't be more than one condition there"
                                lookupTS = "endTS" if list(condition.keys())[0] == "After" else "startTS"
                                use = self.get_use(handling["id"], supplychain["id"], list(condition.values())[0])
                                startingTS = max([use[lookupTS] for id in conditions_ids])
                                candidates_startingTS.append(startingTS)
                            startingTS = max(candidates_startingTS)
                            operation_processed = True

                    if operation_processed:
                        if list(operation["CALCULATION"]["Duration_Type"].keys())[0] == "Fixe":
                            assert operation["CALCULATION"]["Duration_Type"]["Fixe"]["Unit"] == "min", "Not yet implemented : Duration unit is not min"
                            endingTS = startingTS + operation["CALCULATION"]["Duration_Type"]["Fixe"]["Value"]*60
                        elif list(operation["CALCULATION"]["Duration_Type"].keys())[0] == "Amount":
                            assert operation["CALCULATION"]["Duration_Type"]["Amount"]["Unit"] == "%"
                            assert "Value" in machine["SPECIFICATION"]["Throughput"].keys(), "Machine %s is referenced by Amount in Supplychain %s but contains no throughput value." % (machine["id"], supplychain['id'])
                            throughput = machine["SPECIFICATION"]["Throughput"]["Value"]
                            duration_use_hour = operation["CALCULATION"]["Duration_Type"]["Amount"]["Value"] * 1.0 / throughput  # t/hours
                            endingTS = startingTS + duration_use_hour*60*60
                        else:
                            assert False, "Unknown duration type"

                        ids_to_process.remove(id)
                        ids_processed.append(id)
                        startingTS, endingTS = self.get_next_available_TS(machine, startingTS, endingTS)

                        self.uses.append({
                            "startTS": startingTS,
                            "endTS": endingTS,
                            "machine": copy.deepcopy(machine),
                            "handling": copy.deepcopy(handling),
                            "supplychain": copy.deepcopy(supplychain),
                            "operation": copy.deepcopy(operation)
                        })
        return self.uses


    def get_use(self, handlingId, supplychainId, operationId):
        uses = [use for use in self.uses if 
            use["handling"]["id"] == handlingId
            and use["operation"]["id"] == "%s-%s" % (supplychainId, operationId)
        ]
        # print([use["handling"]["id"] for use in self.uses])
        # print([use["operation"]["id"] for use in self.uses])
        # print(handlingId)
        # print(operationId)
        # print(self.uses)
        assert len(uses) == 1, "Undefined uses or multiples use of the same id"
        return uses[0]

    def get_overlapping_TS(self, machine, startTS: int, endTS: int) -> (int, int):
        machine_uses = [use for use in self.uses if machine["id"] == use["machine"]["id"]]
        for use in machine_uses:
            if (
                use["startTS"] < startTS < use["endTS"]
                or use["startTS"] < endTS < use["endTS"]
                or (startTS < use["startTS"] and use["endTS"] < endTS)
            ):
                return use["startTS"], use["endTS"]
        return None, None

    def is_available(self, machine, startTS: int, endTS: int) -> bool:
        return self.get_overlapping_TS(machine, startTS, endTS) == (
            None,
            None,
        )

    def get_next_available_TS(self, machine, startTS: int, endTS: int) -> (int, int):
        while True:
            if self.is_available(machine, startTS, endTS):
                return startTS, endTS
            else:
                _, o_endTS = self.get_overlapping_TS(machine, startTS, endTS)
                delta: int = endTS - startTS
                startTS: int = o_endTS
                endTS: int = startTS + delta