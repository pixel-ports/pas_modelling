import multiprocessing as mp
import psutil
import time
import numpy as np
import matplotlib.pyplot as plt
import argparse
from subprocess import Popen

INTERVAL_SECONDS = 0.1


def monitor(command):
    worker_process = Popen(command.split(" "))
    p = psutil.Process(worker_process.pid)

    cpu_percents = []
    while worker_process.poll() is None:
        cpu_percents.append(p.cpu_percent())
        time.sleep(INTERVAL_SECONDS)

    return np.array(cpu_percents)


def main(command):
    cpu_percents = monitor(command)
    times = np.array(
        list(
            range(
                0,
                int(INTERVAL_SECONDS * 1000 * len(cpu_percents)),
                int(INTERVAL_SECONDS * 1000),
            )
        )
    )
    print("Mean CPU utilization : %02f" % np.mean(cpu_percents / mp.cpu_count()))

    print(cpu_percents / mp.cpu_count())
    plt.xlabel("Time (ms)")
    plt.ylabel("CPU Utilization")
    plt.ylim((0, 100))
    plt.plot(times, cpu_percents / mp.cpu_count())
    plt.show()

    print(cpu_percents)
    plt.xlabel("Time (ms)")
    plt.ylabel("Processing power used")
    plt.ylim((0, 100 * mp.cpu_count()))
    plt.plot(times, cpu_percents)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument("command", type=str, help="Command to monitor")
    args = parser.parse_args()

    main(args.command)
