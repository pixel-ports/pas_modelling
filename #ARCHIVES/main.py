import json
import argparse
import os
import logging

from pas import pas

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")


def main(steps, cargo_handling_requests_path, rules_path, supplychains_path, resources_path, output_path):
    if cargo_handling_requests_path is not None:
        with open(cargo_handling_requests_path, "r") as f:
            cargo_handling_requests = json.loads(f.read())
    if rules_path is not None:
        with open(rules_path, "r") as f:
            rules = json.loads(f.read())
    if supplychains_path is not None:
        with open(supplychains_path, "r") as f:
            supplychains = json.loads(f.read())
    if resources_path is not None:
        with open(resources_path, "r") as f:
            resources = json.loads(f.read())
    pas_output = pas.run(steps, cargo_handling_requests, rules, supplychains, resources)
    with open(output_path, "w") as f:
        f.write(json.dumps(pas_output, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        "--steps", nargs="+", type=int, help="Steps numbers to execute."
    )
    parser.add_argument(
        "--cargo_handling_requests",
        type=str,
        help="Path to the cargo_handling_requests file"
    )
    parser.add_argument(
        "--rules",
        type=str,
        help="Path to the rules file"
    )
    parser.add_argument(
        "--supplychains",
        type=str,
        help="Path to the supplychains file"
    )
    parser.add_argument(
        "--resources",
        type=str,
        help="Path to the resources file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./outputs",
        help="Path of the file that will be created to store output",
    )
    parser.add_argument(
        "--monitor", default=False, action="store_true", help="Start monitoring server"
    )
    args = parser.parse_args()

    main(args.steps, args.cargo_handling_requests, args.rules, args.supplychains, args.resources, args.output)
