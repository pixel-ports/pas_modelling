import json
import argparse
import os
import multiprocessing as mp
import psutil
import time
import shutil
from flask import Flask, request
from flask_restful import Resource, Api
import random

from steps.Step1 import Step1
from steps.Step2 import Step2
from steps.Step3 import Step3
from steps.Step4 import Step4

from typing import List, Dict


def monitor(steps, output_dir):
    class PAS(Resource):
        def get(self):
            subdir = os.path.join(
                output_dir, "%s-%032x" % (str(time.time()), random.getrandbits(128))
            )
            os.mkdir(subdir)
            main(steps, subdir)
            shutil.rmtree(subdir)

    app = Flask(__name__)
    api = Api(app)
    api.add_resource(PAS, "/pas")
    app.run(port="5002")


def main(steps, output_dir):

    if 1 in steps:
        print("--- Step 1 ---")
        with open(os.getenv("PAS_INPUT"), "r") as f:
            pas = json.loads(f.read())
        step1 = Step1(pas)
        pas = step1.run()
        with open(os.path.join(output_dir, "step1_output.json"), "w") as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))

    if 2 in steps:
        print("--- Step 2 ---")
        with open(os.path.join(output_dir, "step1_output.json"), "r") as f:
            pas = json.loads(f.read())
        with open(os.getenv("RULES"), "r") as f:
            rules = json.loads(f.read())
        with open(os.getenv("SUPPLYCHAINS_COLLECTION"), "r") as f:
            supplychains = json.loads(f.read())
        step2 = Step2(pas, rules, supplychains)
        pas = step2.run()
        with open(os.path.join(output_dir, "step2_output.json"), "w") as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))

    if 3 in steps:
        print("--- Step 3 ---")
        with open(os.path.join(output_dir, "step2_output.json"), "r") as f:
            pas = json.loads(f.read())
        with open(os.getenv("SUPPLYCHAINS_COLLECTION"), "r") as f:
            supplychains = json.loads(f.read())
        with open(os.getenv("RESSOURCES_COLLECTION"), "r") as f:
            ressources = json.loads(f.read())
        step3 = Step3(pas, supplychains, ressources)
        pas = step3.run()
        with open(os.path.join(output_dir, "step3_output.json"), "w") as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))

    if 4 in steps:
        print("--- Step 4 ---")
        with open(os.path.join(output_dir, "step3_output.json"), "r") as f:
            pas = json.loads(f.read())
        with open(os.getenv("RESSOURCES_COLLECTION"), "r") as f:
            ressources = json.loads(f.read())
        step4 = Step4(pas, ressources)
        pas = step4.run()
        with open(os.path.join(output_dir, "step4_output.json"), "w") as f:
            f.write(json.dumps(pas, indent=4, ensure_ascii=False))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        "--steps", nargs="+", type=int, help="Steps numbers to execute."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./outputs",
        help="Directory that will be created/overwritten to store output",
    )
    parser.add_argument(
        "--monitor", default=False, action="store_true", help="Start monitoring server"
    )
    args = parser.parse_args()

    if os.path.isdir(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    if args.monitor:
        monitor(args.steps, args.output_dir)
    else:
        main(args.steps, args.output_dir)
