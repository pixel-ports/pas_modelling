from typing import Dict, List, Any

from elements.Supplychain import Supplychain
from elements.Cargo import Cargo

class Machine:

    def __init__(self, data):
        self.identification: Dict[str, Any] = data["identification"]
        self.specifications: Dict[str, Any] = data["specifications"]
        self.constraints: Dict[str, Any] = data["constraints"]
        self.uses: List[Any] = []

    @staticmethod
    def produce_one(machine_dict: Dict[str, Any]) -> "Ship":
        return Machine(machine_dict)

    @staticmethod
    def produce_many(machine_dict_list : List[Dict[str, Any]]) -> List["Ship"]:
        return [Machine.produce_one(machine_dict) for machine_dict in machine_dict_list]

    """throughput is the quantity of material handled per hour (t/h)
    """
    def get_throughput(self, cargo_type: str, distance: float) -> float:
        specifications: Dict = self.get_specifications(cargo_type)
        throughput_operation:float = None
        if distance ==  0:
            throughput_operation = specifications["throughput"]["onSpot"]
        else: # We have a numerical value
            capacity_machine: float = specifications["throughput"]["moving"]["capacity"]
            speed_machine: float = specifications["throughput"]["moving"]["speed"]
            speed_machine_empty: float = self.get_specifications("empty")["throughput"]["moving"]["speed"]
            throughput_operation = capacity_machine / (distance*((1/speed_machine) + (1/speed_machine_empty)))  # TODO Check that it's ok with decimals
        return throughput_operation

    def get_specifications(self, cargo_type: str) -> Dict:
        if cargo_type in self.specifications.keys():
            return self.specifications[cargo_type]
        else:
            return self.specifications["default"]

    def add_unavailable_period(self, startTS: int, endTS: int) -> None:
        assert(self.is_available(startTS, endTS))
        self.constraints["unavailablePeriods"].append({
            "startTS": startTS,
            "endTS": endTS,
            "wording": None
        })

    def get_overlapping_TS(self, startTS: int, endTS: int) -> (int, int):  # TODO Add machine working time constraints
        for period in self.constraints["unavailablePeriods"]:
            if period["startTS"] < startTS < period["endTS"] \
                or period["startTS"] < endTS < period["endTS"] \
                or (startTS < period["startTS"] and period["endTS"] < endTS):
                return period["startTS"], period["endTS"]
        return None, None

    def is_available(self, startTS: int, endTS: int) -> bool:
        return self.get_overlapping_TS(startTS, endTS) == (None, None)  # TODO check return type

    def get_next_available_TS(self, startTS: int, endTS: int) -> (int, int):
        while(True):
            if self.is_available(startTS, endTS):
                return startTS, endTS
            else:
                _, o_endTS = self.get_overlapping_TS(startTS, endTS)
                delta: int = endTS - startTS
                startTS: int = o_endTS
                endTS: int = startTS + delta
    
    def add_use(self, startTS: int, endTS: int, duration: int, operation: Dict, supplychain: Supplychain, cargo: Cargo) -> None:
        self.uses.append({
            "startTS": startTS,
            "endTS": endTS,
            "duration": duration,
            "operation": operation,
            "supplychain": supplychain,
            "cargo": cargo
        })

    def get_timeserie(self) -> Dict:
        timeserie: Dict = {
            "machineID": self.identification["machineID"],
            "uses": []
        }
        for use in self.uses:
            timeserie["uses"].append({
                "startTS": use["startTS"],
                "endTS": use["endTS"],
                "duration": use["duration"],
                "operationID": use["operation"]["id"],
                "operationName": use["operation"]["name"],
                "supplychainID": use["supplychain"].identification["name"],  # TODO Set an ID instead of the name
                "cargoID": use["cargo"].ship["shipID"]
            })
        return timeserie