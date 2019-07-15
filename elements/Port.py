from Activity import Activity

import uuid
import time
import json

class Port():
    
    def __init__(self, cargoes, machines, supplychains):
        self.cargoes = cargoes
        self.machines = machines
        self.supplychains = supplychains
        self.activites = None
        self.machine_set = None
        self.pas = None

    def build_pas(self):
        self.cargoes = self.step_1()
        self.activites = self.step_2()
        self.machine_set = self.step_3()
        self.pas = self.generate_PAS()

    def get_machine(self, id):
        return next((machine for machine in self.machines if machine.identification["machineID"] == id), None)

    def get_default_supplychain(self):
        default_supplychains = [sc for sc in self.supplychains if sc.identification["name"] == "defaultSupplychain"]
        assert len(default_supplychains) <= 1, "There couldn't be more than one default supplychain"
        return default_supplychains[0] if len(default_supplychains)==1 else None

    
    
    def step_1(self):
        return sorted(self.cargoes, key=lambda x: -x.constraint["priority"])

    def step_2(self):
        self.activites = []

        for cargo in self.cargoes:
            selected_supplychain, mapping_type = cargo.map_supplychain[0]
            if mapping_type == "default":
                selected_supplychain = self.get_default_supplychain()

            self.activites.append(Activity({
                "pair": {
                    "cargo": cargo,
                    "supplychain": selected_supplychain,
                    "mappingType": mapping_type
                },
                "logs": {
                    "comments": [],
                    "modifications": []
                }
            }))

    def step_3(self):
        machine_set = set()
        for activity in self.activites:
            cargo = activity.pair["cargo"]
            startingTS = cargo["ship"]["arrivingTime"]  # TODO Implement setup duration
            for operation in activity.pair["supplychain"]["operationsSequence"]:
                machine = self.get_machine(operation["machineID"])
                throughput_operation = machine.get_throughput(cargo.cargo["type"], operation["distance"])
                duration_use = cargo.cargo["amount"]/throughput_operation

                endingTS = startingTS + duration_use  # TODO Implement other operations specific durations
                startingTS, endingTS = machine.get_next_available_TS(startingTS, endingTS)
                machine.add_unavailable_period(startingTS, endingTS)


                operation["startingTS"] = startingTS
                operation["endingTS"] = endingTS

                startingTS = operation["endingTS"]  # For next loop

                machine.add_use(
                    operation["startingTS"],
                    operation["endTS"],
                    duration_use,
                    activity.pair["supplychain"],
                    activity.pair["cargo"]
                )

                machine_set.add(machine)
        return machine_set

    def generate_PAS(self):
        pas = {
            "metadata": {
                "pasID": uuid.uuid4(),
                "creationTS": int(time.time()),
                "creatorID": "rquera",
                "status": None,
                "parents": {
                    "cargoQueueID": None,  # TODO Generate hash for the input json file
                    "supplychainCollectionID": None,
                    "activitiesQueueID": None,
                    "machineCollectionID": None
                },
                "logs": {
                    "comments": [],
                    "modifications": []
                }
            },
            "timeseries": []
        }

        for machine in self.machine_set:
            pas["timeseries"].append(machine.get_timeserie())

        return pas

    def export_pas(self, filepath):
        with open("pas.json", "w") as f:
            f.write(json.dumps(self.pas, indent=4))
