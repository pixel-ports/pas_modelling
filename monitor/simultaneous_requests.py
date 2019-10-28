import time
import numpy as np
import matplotlib.pyplot as plt
import argparse
import dask
from subprocess import Popen

INTERVAL_SECONDS = 0.1

def monitor(command):
    begin_time = time.time()
    worker_process = Popen(command.split(" "))
    while worker_process.poll() is None:
        time.sleep(INTERVAL_SECONDS)
    return time.time() - begin_time

def parallel_works(nb_processes, command):
    works = [dask.delayed(work)() for i in range(nb_processes)]
    mean_time = dask.delayed(np.mean)(works)
    return mean_time.compute(scheduler="processes")


def main(min_processes, max_processes, step_processes, command):
    x, y = [], []
    for nb_processes in range(min_processes, max_processes, step_processes):
        print("Test with %d processes." % nb_processes)
        x.append(nb_processes)
        y.append(round(parallel_works(nb_processes, is_test), 2))
        print("  ==> %f" % y[-1])

    print(x)
    print(y)
    plt.plot(x, y)
    plt.show


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        "--min_processes",
        type=int,
        help="Max number of process to simultaneously start.",
    )
    parser.add_argument(
        "--max_processes",
        type=int,
        help="Max number of process to simultaneously start.",
    )
    parser.add_argument(
        "--step_processes", type=int, help="Step number of processes to increment."
    )
    parser.add_argument(
        "command", type=str, help="Evaluate simultaneous requests on a test workflow"
    )
    args = parser.parse_args()

    main(args.min_processes, args.max_processes, args.step_processes, args.command)
