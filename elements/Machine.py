from typing import Dict, List, Any

class Machine:

    def __init__(self, data):
        self.identification: Dict[str, Any] = data.identification
        self.specifications: Dict[str, Any] = data.specifications
        self.constraints: Dict[str, Any] = data.constraints
        self.uses: List[Any] = []

    @staticmethod
    def produce_one(machine_dict: Dict[str, Any]) -> "Ship":
        return Machine(machine_dict)

    @staticmethod
    def produce_many(machine_dict_list : List[Dict[str, Any]]) -> List["Ship"]:
        return [Machine.produce_one(machine_dict) for machine_dict in machine_dict_list]

    """throughput is the quantity of material handled per hour (t/h)
    """
    def get_throughput(self, cargo_type, distance):
        if distance ==  0:
            throughput_operation = self.specifications[cargo_type]["throughput"]["onSpot"]
        else: # We have a numerical value
            capacity_machine = self.specifications[cargo_type]["throughput"]["moving"]["capacity"]
            speed_machine = self.specifications[cargo_type]["throughput"]["moving"]["speed"]
            speed_machine_empty = self.specifications["empty"]["throughput"]["moving"]["speed"]
            throughput_operation = capacity_machine / (distance*((1/speed_machine) + (1/speed_machine_empty)))  # TODO Check that it's ok with decimals
        return throughput_operation

    def add_unavailable_period(self, startTS, endTS):
        assert(self.is_available(startTS, endTS))
        self.constraints["unavailablePeriods"].append({
            "startTS": startTS,
            "endTS": endTS,
            "wording": None
        })

    def get_overlapping_TS(self, startTS, endTS):  # TODO Add machine working time constraints
        for period in self.constraints["unavailablePeriods"]:
            if period["startTS"] < startTS < period["endTS"] \
                or period["startTS"] < endTS < period["endTS"] \
                or (startTS < period["startTS"] and period["endTS"] < endTS):
                return period["startTS"], period["endTS"]
        return None, None

    def is_available(self, startTS, endTS):
        return self.get_overlapping_TS(startTS, endTS) == (None, None)  # TODO check return type

    def get_next_available_TS(self, startTS, endTS):
        while(True):
            if self.is_available(startTS, endTS):
                return startTS, endTS
            else:
                _, o_endTS = self.get_overlapping_TS(startTS, endTS)
                delta = endTS - startTS
                startTS = o_endTS
                endTS = startTS + delta
    
    def add_use(self, startTS, endTS, duration, supplychain, cargo):
        self.uses.append({
            "startTS": startTS,
            "endTS": endTS,
            "duration": duration,
            "supplychain": supplychain,
            "cargo": cargo
        })

    def get_timeserie(self):
        timeserie = []
        for use in self.uses:
            timeserie.append({
                "startTS": use["startTS"],
                "endTS": use["endTS"],
                "duration": use["duration"],
                "supplychainID": use["supplychain"].identification["name"],  # TODO Set an ID instead of the name
                "cargoID": use["cargo"].ship["shipID"]
            })
        return timeserie