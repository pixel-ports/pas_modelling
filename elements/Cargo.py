from typing import Dict, List, Any

from elements.Supplychain import Supplychain

class Cargo:
    
    def __init__(self, data):
        self.ship: Dict[str, Any] = data["ship"]
        self.cargo: Dict[str, Any] = data["cargo"]
        self.constraint: Dict[str, Any] = data["constraint"]
        self.logs: Dict[str, List[str]] = data["logs"]
    
    @staticmethod
    def produce_one(cargo_dict: Dict[str, Any]) -> "Cargo":
        return Cargo(cargo_dict)

    @staticmethod
    def produce_many(cargo_dict_list : List[Dict[str, Any]]) -> List["Cargo"]:
        return [Cargo.produce_one(cargo_dict) for cargo_dict in cargo_dict_list]

    def map_supplychain(self, supplychains) -> (Supplychain, str):
        filtered_supplychains: List[Supplychain] = [sc for sc in supplychains if (self.cargo["type"] in sc.identification["suitableCargoType"])]

        selected_supplychain: Supplychain = None  # Default if no supplychain is matched
        mapping_type: str = "default"
        
        if len(filtered_supplychains) == 1:
            selected_supplychain = filtered_supplychains[0]
            mapping_type = "direct"
        elif len(filtered_supplychains)>1:
            max_priority: int = max([sc.identification["priority"] for sc in filtered_supplychains])
            max_priority_chains: List[Supplychain] = [sc for sc in filtered_supplychains if sc.identification["priority"] == max_priority]
            if len(max_priority_chains) == 1:
                selected_supplychain = max_priority_chains[0]
                mapping_type = "priorized"
        
        return selected_supplychain, mapping_type
