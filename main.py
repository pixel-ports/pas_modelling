import json
from elements.Cargo import Cargo
from elements.Machine import Machine
from elements.Supplychain import Supplychain
from elements.Port import Port

from typing import List, Dict

if __name__ == "__main__":

    with open("data/ships_call_list.json","r") as f:
        data: Dict = json.loads(f.read())
    ships: List[Cargo] = Cargo.produce_many(data)
    
    with open("data/supplychain_collection.json", "r") as f:
        data: Dict = json.loads(f.read())
    supplychains: List[Supplychain] = Supplychain.produce_many(data)

    with open("data/machine_collection.json","r") as f:
        data: Dict = json.loads(f.read())
    machines: List[Machine] = Machine.produce_many(data)

    port: Port = Port(ships, machines, supplychains)
    port.build_pas()
    port.export_pas("pas.json")