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

    if os.path.isdir(os.getenv("OUTPUT_DIRECTORY")):
        shutil.rmtree(os.getenv("OUTPUT_DIRECTORY"))
    os.mkdir(os.getenv("OUTPUT_DIRECTORY"))

    with open(os.getenv("PAS_INPUT"), "r") as f:
        pas_input = json.loads(f.read())
    step1 = Step1(pas_input)
    pas_input = step1.run()
    with open(
        os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step1_output.json"), "w"
    ) as f:
        f.write(json.dumps(pas_input, indent=4, ensure_ascii=False))

    with open(
        os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step1_output.json"), "r"
    ) as f:
        pas_input = json.loads(f.read())
    with open(os.getenv("SUPPLYCHAINS_COLLECTION"), "r") as f:
        supplychains = json.loads(f.read())
    step2 = Step2(pas_input, supplychains)
    pas_input = step2.run()
    with open(
        os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step2_output.json"), "w"
    ) as f:
        f.write(json.dumps(pas_input, indent=4, ensure_ascii=False))

    with open(
        os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step2_output.json"), "r"
    ) as f:
        pas_input = json.loads(f.read())
    with open(os.getenv("MACHINES_COLLECTION"), "r") as f:
        machines = json.loads(f.read())
    step3 = Step3(pas_input, machines)
    uses = step3.run()
    with open(
        os.path.join(os.getenv("OUTPUT_DIRECTORY"), "step3_output.json"), "w"
    ) as f:
        f.write(json.dumps(uses, indent=4, ensure_ascii=False))


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
