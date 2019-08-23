from typing import Dict, List


class MachinesCollection:
    def __init__(self, list):
        self.list: List = list
        self.uses: Dict = {}
        for machine in self.list:
            self.uses[machine["identification"]["id"]] = []

    def get(self, id: int) -> Dict:
        return next(
            (machine for machine in self.list if machine["identification"]["id"] == id),
            None,
        )

    """throughput is the quantity of material handled per hour (t/h)
    """

    def get_throughput(self, machine, cargo_type: str, distance: float) -> float:
        specifications: Dict = self.get_specifications(machine, cargo_type)
        throughput_operation: float = None
        if distance == 0:
            throughput_operation = specifications["throughput"]["onSpot"]
        else:  # We have a numerical value
            capacity_machine: float = specifications["throughput"]["moving"]["capacity"]
            speed_machine: float = specifications["throughput"]["moving"]["speed"]
            speed_machine_empty: float = self.get_specifications(machine, "empty")[
                "throughput"
            ]["moving"]["speed"]
            throughput_operation = capacity_machine / (
                distance * ((1 / speed_machine) + (1 / speed_machine_empty))
            )  #  TODO Check that it's ok with decimals
        return throughput_operation

    def get_specifications(self, machine, cargo_type: str) -> Dict:
        if cargo_type in machine["specifications"].keys():
            return machine["specifications"][cargo_type]
        else:
            return machine["specifications"]["default"]

    def add_unavailable_period(self, machine, startTS: int, endTS: int) -> None:
        assert self.is_available(machine, startTS, endTS)
        machine["constraints"]["unavailablePeriods"].append(
            {"startTS": startTS, "endTS": endTS, "wording": None}
        )

    def get_overlapping_TS(
        self, machine, startTS: int, endTS: int
    ) -> (int, int):  #  TODO Add machine working time constraints
        for period in machine["constraints"]["unavailablePeriods"]:
            if (
                period["startTS"] < startTS < period["endTS"]
                or period["startTS"] < endTS < period["endTS"]
                or (startTS < period["startTS"] and period["endTS"] < endTS)
            ):
                return period["startTS"], period["endTS"]
        return None, None

    def is_available(self, machine, startTS: int, endTS: int) -> bool:
        return self.get_overlapping_TS(machine, startTS, endTS) == (
            None,
            None,
        )  #  TODO check return type

    def get_next_available_TS(self, machine, startTS: int, endTS: int) -> (int, int):
        while True:
            if self.is_available(machine, startTS, endTS):
                return startTS, endTS
            else:
                _, o_endTS = self.get_overlapping_TS(machine, startTS, endTS)
                delta: int = endTS - startTS
                startTS: int = o_endTS
                endTS: int = startTS + delta

    def add_use(
        self,
        machine,
        startTS: int,
        endTS: int,
        duration: int,
        operation: Dict,
        supplychain: Dict,
        cargo: Dict,
    ) -> None:
        self.uses[machine["identification"]["id"]].append(
            {
                "startTS": startTS,
                "endTS": endTS,
                "duration": duration,
                "operation": operation,
                "supplychain": supplychain,
                "cargo": cargo,
            }
        )

    def get_timeserie(self, machine) -> Dict:
        timeserie: Dict = {"machineId": machine["identification"]["id"], "uses": []}
        for use in self.uses[timeserie["machineId"]]:
            timeserie["uses"].append(
                {
                    "startTS": use["startTS"],
                    "endTS": use["endTS"],
                    "duration": use["duration"],
                    "operationID": use["operation"]["id"],
                    "operationName": use["operation"]["name"],
                    "supplychainID": use["supplychain"]["identification"][
                        "name"
                    ],  #  TODO Set an ID instead of the name
                    "cargoID": use["cargo"]["ship"]["id"],
                }
            )
        return timeserie
