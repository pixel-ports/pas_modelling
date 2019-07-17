from elements.Activity import Activity
from elements.Cargo import Cargo
from elements.Machine import Machine
from elements.Supplychain import Supplychain
from elements.Activity import Activity

import uuid
import time
import json
from typing import List, Dict, Set, Any

class Port():
    
    def __init__(self, cargoes: List[Cargo], machines: List[Machine], supplychains: List[Supplychain]):
        self.cargoes: List[Cargo] = cargoes
        self.machines: List[Machine] = machines
        self.supplychains: List[Supplychain] = supplychains
        self.activities: List[Activity] = None
        self.machine_set: Set(Machine) = None
        self.pas: Dict[str, Any] = None

    """Construct the PAS dictionnary
    """
    def build_pas(self) -> None:
        self.cargoes = self.step_1()
        self.activities = self.step_2()
        self.machine_set = self.step_3()
        self.pas = self.generate_PAS()

    def get_machine(self, id: int) -> Machine:
        return next((machine for machine in self.machines if machine.identification["machineID"] == id), None)

    """Assert that there is a default supplychain defined for the port and return it
    
    Returns:
        Supplychain -- The default Supplychain
    """
    def get_default_supplychain(self) -> Supplychain:
        default_supplychains = [sc for sc in self.supplychains if sc.identification["name"] == "defaultSupplychain"]
        assert len(default_supplychains) <= 1, "There couldn't be more than one default supplychain"
        return default_supplychains[0] if len(default_supplychains)==1 else None
    
    """Sort cargoes according to their priority
    
    Returns:
        List[Cargo] -- The ordered list of cargoes
    """
    def step_1(self) -> List[Cargo]:
        return sorted(self.cargoes, key=lambda x: -x.constraint["priority"])

    """Pair cargoes and supplychains
    
    Returns:
        List[Activity] -- The activity list pairing cargoes and supplychains
    """
    def step_2(self) -> List[Activity]:
        activities: List[Activity] = []

        for cargo in self.cargoes:
            selected_supplychain, mapping_type = cargo.map_supplychain(self.supplychains)
            if mapping_type == "default":
                selected_supplychain = self.get_default_supplychain()

            activities.append(Activity.produce_one({
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
        return activities

    """Build the machines timestamps that are used for the processing of the cargoes for the port
    
    Returns:
        Set[Machine] -- The set of Machines involved
    """
    def step_3(self) -> Set[Machine]:
        machine_set: Set[Machine] = set()
        for activity in self.activities:
            cargo: Cargo = activity.pair["cargo"]
            startingTS: int = cargo.ship["arrivingTime"]  # TODO Implement setup duration
            supplychain: Supplychain = activity.pair["supplychain"]
            for operation in supplychain.operationsSequence:
                machine: Machine = self.get_machine(operation["machineID"])
                operation["throughput"]: float = machine.get_throughput(cargo.cargo["type"], operation["distance"])
                duration_use: int = cargo.cargo["amount"]/operation["throughput"]

                startingTS = supplychain.adjust_starting_ts(operation, startingTS)
                endingTS: int = startingTS + duration_use  # TODO Implement other operations specific durations
                startingTS, endingTS = machine.get_next_available_TS(startingTS, endingTS)
                machine.add_unavailable_period(startingTS, endingTS)


                operation["startingTS"] = startingTS
                operation["endingTS"] = endingTS

                startingTS = operation["endingTS"]  # For next loop

                machine.add_use(
                    operation["startingTS"],
                    operation["endingTS"],
                    duration_use,
                    operation,
                    activity.pair["supplychain"],
                    activity.pair["cargo"]
                )

                machine_set.add(machine)
        return machine_set

    """Create the PAS dictionnary
    
    Returns:
        Dict -- The PAS dictionnary
    """
    def generate_PAS(self) -> Dict:
        pas: Dict = {
            "metadata": {
                "pasID": str(uuid.uuid4()),
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

    """Save PAS to file
    """
    def export_pas(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            f.write(json.dumps(self.pas, indent=4))
