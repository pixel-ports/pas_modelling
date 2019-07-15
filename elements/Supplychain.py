from typing import Dict, List, Any

class Supplychain():

    def __init__(self, data: Dict[str, Any]):
        self.identification: Dict[str, Any] = data["identification"]
        self.operationsSequence: Dict[str, Any] = data["operationsSequence"]
        
    @staticmethod
    def produce_one(supplychain_dict: Dict[str, Any]) -> "Supplychain":
        return Supplychain(supplychain_dict)

    @staticmethod
    def produce_many(supplychain_dict_list : List[Dict[str, Any]]) -> List["Supplychain"]:
        return [Supplychain.produce_one(supplychain_dict) for supplychain_dict in supplychain_dict_list]
