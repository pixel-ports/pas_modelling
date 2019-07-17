from typing import Dict, List, Any

class Supplychain():

    def __init__(self, data: Dict[str, Any]):
        self.identification: Dict[str, Any] = data["identification"]
        self.operationsSequence: List[Dict[str, Any]] = data["operationsSequence"]
        
    @staticmethod
    def produce_one(supplychain_dict: Dict[str, Any]) -> "Supplychain":
        return Supplychain(supplychain_dict)

    @staticmethod
    def produce_many(supplychain_dict_list : List[Dict[str, Any]]) -> List["Supplychain"]:
        return [Supplychain.produce_one(supplychain_dict) for supplychain_dict in supplychain_dict_list]

    def get_operation(self, operation_id: int) -> Dict:
        filtered_operations = [op for op in self.operationsSequence if op["id"] == operation_id]
        assert len(filtered_operations) == 1, "operation ids should be uniques"
        return filtered_operations[0]

    def get_previous_operation(self, operation_id: int) -> Dict:
        for i in range(len(self.operationsSequence)):
            if self.operationsSequence[i]["id"] == operation_id:
                return self.operationsSequence[i-1]
        raise Exception("Can't get the previous operation if that's the first one")

    def adjust_starting_ts(self, operation: Dict, starting_ts):
        if operation["startOption"]["type"] == "fixedDelay":
            return starting_ts + operation["startOption"]["value"]
        elif operation["startOption"]["type"] == "withOperation":
            target_operation = self.get_operation(operation["startOption"]["value"])
            assert target_operation["statingTS"] != None, "Operations should be placed in chronological order"
            return target_operation["startingTS"]
        elif operation["startOption"]["type"] == "afterOperation":
            target_operation = self.get_operation(operation["startOption"]["value"])
            assert target_operation["endingTS"] != None, "Operations should be placed in chronological order"
            return target_operation["endingTS"]
        elif operation["startOption"]["type"] == "amountThreshold":
            target_operation = self.get_previous_operation(operation["id"])
            assert target_operation["startingTS"] != None, "Operations should be placed in chronological order"
            assert target_operation["throughput"] != None, "Operations should be placed in chronological order"
            return target_operation["startingTS"] + operation["value"]/target_operation("throughput")
        elif operation["startOption"]["type"] == "fixedTimestamp":
            return operation["startOption"]["value"]
        else:
            raise Exception("Unknown operation startType : %s" % operation["startOption"]["type"])
