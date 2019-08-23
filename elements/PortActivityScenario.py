from elements.ShipsCallList import ShipsCallList
from elements.CargoesQueue import CargoesQueue
from elements.ActivitiesQueue import ActivitiesQueue
from elements.MachinesCollection import MachinesCollection
from elements.SupplychainsCollection import SupplychainsCollection

import uuid
import time
import json
import os
from typing import List, Dict, Set, Any


class PortActivityScenario:
    def __init__(
        self,
        ships_call_list: ShipsCallList,
        machines_collection: MachinesCollection,
        supplychains_collection: SupplychainsCollection,
    ):
        self.ships_call_list: ShipsCallList = ships_call_list
        self.machines_collection: MachinesCollection = machines_collection
        self.supplychains_collection: SupplychainsCollection = supplychains_collection
        self.cargoes_queue: CargoesQueue = None
        self.activities_queue: ActivitiesQueue = None
        self.machines_set: MachineSet = None
        self.dict: Dict = None

    def execute_step(self, step: int) -> None:
        if step == 1:
            self.cargoes_queue = self.step_1()
            self.export_to_json(self.cargoes_queue.list, os.getenv("CARGOES_QUEUE"))
        elif step > 1:
            with open(os.getenv("CARGOES_QUEUE"), "r") as f:
                list: List = json.loads(f.read())
            self.cargoes_queue = CargoesQueue(list)

        if step == 2:
            self.activities_queue = self.step_2()
            self.export_to_json(
                self.activities_queue.list, os.getenv("ACTIVITIES_QUEUE")
            )
        elif step > 2:
            with open(os.getenv("ACTIVITIES_QUEUE"), "r") as f:
                list: List = json.loads(f.read())
            self.activities_queue = ActivitiesQueue(list)

        if step == 3:
            self.dict = self.step_3()
            self.export_to_json(self.dict, os.getenv("PORT_ACTIVITY_SCENARIO"))
        elif step > 3:
            with open(os.getenv("PORT_ACTIVITY_SCENARIO"), "r") as f:
                dict: Dict = json.loads(f.read())
            self.dict = dict

    def execute_all_steps(self) -> None:
        self.execute_step(1)
        self.execute_step(2)
        self.execute_step(3)

    """Sort cargoes according to their priority
    
    Returns:
        List[Cargo] -- The ordered list of cargoes
    """

    def step_1(self) -> CargoesQueue:
        cargoes: List[Dict] = []
        for ship in self.ships_call_list.list:
            for cargo in ship["cargoes"]:
                new_cargo = cargo.copy()
                new_cargo["ship"] = {
                    "id": ship["id"],
                    "arrivingTime": ship["arrivingTime"],
                    "berthAllocation": ship["berthAllocation"],
                    "constraints": ship["constraints"],
                }
                new_cargo["logs"] = {"comments": [], "modifications": []}
                cargoes.append(new_cargo)

        return CargoesQueue(
            sorted(cargoes, key=lambda x: -x["ship"]["constraints"]["priority"])
        )

    """Pair cargoes and supplychains
    
    Returns:
        List[Activity] -- The activity list pairing cargoes and supplychains
    """

    def step_2(self) -> ActivitiesQueue:
        activities: List[Dict] = []

        for cargo in self.cargoes_queue.list:
            selected_supplychain, mapping_type = self.supplychains_collection.map_supplychain(
                cargo
            )
            if mapping_type == "default":
                selected_supplychain = self.supplychains_collection.get_default()

            activities.append(
                {
                    "pair": {
                        "cargo": cargo,
                        "supplychain": selected_supplychain,
                        "mappingType": mapping_type,
                    },
                    "logs": {"comments": [], "modifications": []},
                }
            )
        return ActivitiesQueue(activities)

    """Build the machines timestamps that are used for the processing of the cargoes for the port
    
    Returns:
        Set[Machine] -- The set of Machines involved
    """

    def step_3(self) -> "PortActivityScenario":
        machines: Dict = {}  # Acts as a Set (because dict is unhashable in python)
        for activity in self.activities_queue.list:
            cargo: Dict = activity["pair"]["cargo"]
            startingTS: int = cargo["ship"][
                "arrivingTime"
            ]  #  TODO Implement setup duration
            supplychain: Dict = activity["pair"]["supplychain"]
            for operation in supplychain["operationsSequence"]:
                machine: Dict = self.machines_collection.get(operation["machineId"])
                operation[
                    "throughput"
                ]: float = self.machines_collection.get_throughput(
                    machine, cargo["type"], operation["distance"]
                )
                duration_use: int = cargo["amount"] / operation["throughput"]

                startingTS = self.supplychains_collection.adjust_starting_ts(
                    supplychain, operation, startingTS
                )
                endingTS: int = startingTS + duration_use  #  TODO Implement other operations specific durations
                startingTS, endingTS = self.machines_collection.get_next_available_TS(
                    machine, startingTS, endingTS
                )
                self.machines_collection.add_unavailable_period(
                    machine, startingTS, endingTS
                )

                operation["startingTS"] = startingTS
                operation["endingTS"] = endingTS

                startingTS = operation["endingTS"]  #  For next loop

                self.machines_collection.add_use(
                    machine,
                    operation["startingTS"],
                    operation["endingTS"],
                    duration_use,
                    operation,
                    activity["pair"]["supplychain"],
                    activity["pair"]["cargo"],
                )

                machines[machine["identification"]["id"]] = machine

        pas_dict: Dict = {
            "metadata": {
                "pasID": str(uuid.uuid4()),
                "creationTS": int(time.time()),
                "creatorID": "rquera",
                "status": None,
                "parents": {
                    "cargoQueueID": None,  #  TODO Generate hash for the input json file
                    "supplychainCollectionID": None,
                    "activitiesQueueID": None,
                    "machineCollectionID": None,
                },
                "logs": {"comments": [], "modifications": []},
            },
            "timeseries": [],
        }

        for _, machines in machines.items():
            pas_dict["timeseries"].append(
                self.machines_collection.get_timeserie(machine)
            )
        return pas_dict

    """Save object to file
    """

    def export_to_json(self, obj, filepath: str) -> None:
        with open(filepath, "w") as f:
            f.write(json.dumps(obj, indent=4))
