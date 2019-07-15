import json
from elements.Cargo import Cargo
from elements.Machine import Machine
from elements.Supplychain import Supplychain
from elements.Port import Port

if __name__ == "__main__":

    with open("ships_call_list.json","r") as f:
        data = json.loads(f.read())
    ships = Cargo.produce_many(data)
    
    with open("supply-chain_collection.json", "r") as f:
        data = json.loads(f.read())
    supplychains = Supplychain.produce_many(data)

    with open("machine_collection.json","r") as f:
        data = json.loads(f.read())
    machines = Machine.produce_many(data)

port = Port(ships, machines, supplychains)