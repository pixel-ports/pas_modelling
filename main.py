import json
import argparse
import os
import multiprocessing as mp
import psutil
import time
import shutil

from steps.Step1 import Step1
from steps.Step2 import Step2
from steps.Step3 import Step3
from steps.Step4 import Step4

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

    if 1 in steps:
        print("--- Step 1 ---")
        with open(os.getenv("PAS_INPUT"), "r") as f:
            pas = json.loads(f.read())
        step1 = Step1(pas)
        pas = step1.run()
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step1_output.json"), "w"
        ) as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))

    if 2 in steps:
        print("--- Step 2 ---")
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step1_output.json"), "r"
        ) as f:
            pas = json.loads(f.read())
        with open(os.getenv("SUPPLYCHAINS_COLLECTION"), "r") as f:
            supplychains = json.loads(f.read())
        step2 = Step2(pas, supplychains)
        pas = step2.run()
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step2_output.json"), "w"
        ) as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))

    if 3 in steps:
        print("--- Step 3 ---")
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step2_output.json"), "r"
        ) as f:
            pas = json.loads(f.read())
        with open(os.getenv("MACHINES_COLLECTION"), "r") as f:
            machines = json.loads(f.read())
        step3 = Step3(pas, machines)
        pas = step3.run()
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step3_output.json"), "w"
        ) as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))

    if 4 in steps:
        print("--- Step 4 ---")
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step3_output.json"), "r"
        ) as f:
            pas = json.loads(f.read())
        with open(os.getenv("MACHINES_COLLECTION"), "r") as f:
            machines = json.loads(f.read())
        step4 = Step4(pas, machines)
        pas = step4.run()
        with open(
            os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step4_output.json"), "w"
        ) as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        "--steps", nargs="+", type=int, help="Steps numbers to execute."
    )
    parser.add_argument("--monitor_cpu", type=bool, help="Monitor cpu usage")
    args = parser.parse_args()

    if args.monitor_cpu:
        cpu_percents = monitor(main, (args.steps,))
        print(cpu_percents)
    else:
        main(args.steps)
