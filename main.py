import json
import argparse
import os
import multiprocessing as mp
import psutil
import time

from elements.ShipsCallList import ShipsCallList
from elements.SupplychainsCollection import SupplychainsCollection
from elements.MachinesCollection import MachinesCollection
from elements.PortActivityScenario import PortActivityScenario

from typing import List, Dict

def monitor(target, args):
    worker_process = mp.Process(target=target, args=args)
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    cpu_percents = []
    while worker_process.is_alive():
        cpu_percents.append(p.cpu_percent())
        time.sleep(0.1)

    worker_process.join()
    return cpu_percents


def main(steps):
    with open(os.getenv("SHIPS_CALL_LIST"), "r") as f:
        list: List = json.loads(f.read())
    ships_call_list: ShipsCallList = ShipsCallList(list)

    with open(os.getenv("SUPPLYCHAINS_COLLECTION"), "r") as f:
        list: List = json.loads(f.read())
    supplychains_collection: SupplychainsCollection = SupplychainsCollection(list)

    with open(os.getenv("MACHINES_COLLECTION"), "r") as f:
        list: List = json.loads(f.read())
    machines_collection: MachinesCollection = MachinesCollection(list)

    port_activity_scenario: PortActivityScenario = PortActivityScenario(
        ships_call_list, machines_collection, supplychains_collection
    )
    if args.step is not None:
        port_activity_scenario.execute_step(args.step)
    else:
        port_activity_scenario.execute_all_steps()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument("--step", nargs="?", type=int, help="Step number to execute.")
    parser.add_argument("--monitor_cpu", type=bool, help="Monitor cpu usage")
    args = parser.parse_args()

    if args.monitor_cpu:
        cpu_percents = monitor(main, (args.step,))
        print(cpu_percents)
    else:
        main(args.step)
