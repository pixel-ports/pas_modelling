from typing import Dict


class SupplychainsCollection:
    def __init__(self, list):
        self.list = list

    """Assert that there is a default supplychain defined for the port and return it
    
    Returns:
        Supplychain -- The default Supplychain
    """

    def get_default(self) -> Dict:
        default_supplychains = [
            sc
            for sc in self.list
            if sc["identification"]["name"] == "defaultSupplychain"
        ]
        assert (
            len(default_supplychains) <= 1
        ), "There couldn't be more than one default supplychain"
        return default_supplychains[0] if len(default_supplychains) == 1 else None

    def map_supplychain(self, cargo) -> (Dict, str):
        filtered_supplychains: List[Dict] = [
            sc
            for sc in self.list
            if (cargo["type"] in sc["identification"]["suitableCargoType"])
        ]

        selected_supplychain: Dict = None  #  Default if no supplychain is matched
        mapping_type: str = "default"

        if len(filtered_supplychains) == 1:
            selected_supplychain = filtered_supplychains[0]
            mapping_type = "direct"
        elif len(filtered_supplychains) > 1:
            max_priority: int = max(
                [sc["identification"]["priority"] for sc in filtered_supplychains]
            )
            max_priority_chains: List[Dict] = [
                sc
                for sc in filtered_supplychains
                if sc["identification"]["priority"] == max_priority
            ]
            if len(max_priority_chains) == 1:
                selected_supplychain = max_priority_chains[0]
                mapping_type = "priorized"

        return selected_supplychain, mapping_type

    def get_operation(self, supplychain, operation_id: int) -> Dict:
        filtered_operations = [
            op for op in supplychain["operationsSequence"] if op["id"] == operation_id
        ]
        assert len(filtered_operations) == 1, "operation ids should be uniques"
        return filtered_operations[0]

    def get_previous_operation(self, supplychain, operation_id: int) -> Dict:
        for i in range(len(supplychain["operationsSequence"])):
            if supplychain["operationsSequence"][i]["id"] == operation_id:
                return supplychain["operationsSequence"][i - 1]
        raise Exception("Can't get the previous operation if that's the first one")

    def adjust_starting_ts(self, supplychain: Dict, operation: Dict, starting_ts: int):
        if operation["startOption"]["type"] == "fixedDelay":
            return starting_ts + operation["startOption"]["value"]
        elif operation["startOption"]["type"] == "withOperation":
            target_operation = self.get_operation(
                supplychain, operation["startOption"]["value"]
            )
            assert (
                target_operation["statingTS"] != None
            ), "Operations should be placed in chronological order"
            return target_operation["startingTS"]
        elif operation["startOption"]["type"] == "afterOperation":
            target_operation = self.get_operation(
                supplychain, operation["startOption"]["value"]
            )
            assert (
                target_operation["endingTS"] != None
            ), "Operations should be placed in chronological order"
            return target_operation["endingTS"]
        elif operation["startOption"]["type"] == "amountThreshold":
            target_operation = self.get_previous_operation(supplychain, operation["id"])
            assert (
                target_operation["startingTS"] != None
            ), "Operations should be placed in chronological order"
            assert (
                target_operation["throughput"] != None
            ), "Operations should be placed in chronological order"
            return target_operation["startingTS"] + operation[
                "value"
            ] / target_operation("throughput")
        elif operation["startOption"]["type"] == "fixedTimestamp":
            return operation["startOption"]["value"]
        else:
            raise Exception(
                "Unknown operation startType : %s" % operation["startOption"]["type"]
            )
