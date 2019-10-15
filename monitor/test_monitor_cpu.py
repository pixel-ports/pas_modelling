import multiprocessing as mp
import psutil
import time
import numpy as np
import matplotlib.pyplot as plt

INTERVAL_SECONDS = 0.1


def monitor(target):  # https://stackoverflow.com/a/49212252/6463920
    worker_process = mp.Process(target=target)
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    cpu_percents = []
    while worker_process.is_alive():
        cpu_percents.append(p.cpu_percent())
        time.sleep(INTERVAL_SECONDS)

    worker_process.join()
    return np.array(cpu_percents)


def main():
    nb = 30000000

    a = list(range(nb))
    for i in a:
        i = i + 1
    for i in range(nb):
        a.pop()


if __name__ == "__main__":
    cpu_percents = monitor(main)
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
