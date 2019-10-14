import time
import numpy as np
import matplotlib.pyplot as plt
import argparse
import dask

INTERVAL_SECONDS = 0.1  

def work():  # Takes a bit less than 4 seconds to execute
    begin_time = time.time()
    nb = 30000000
    a = list(range(nb))
    for i in a:
        i = i + 1
    for i in range(nb):
        a.pop()
    return time.time()-begin_time

def parallel_works(nb_processes):
    works = [dask.delayed(work)() for i in range(nb_processes)]
    mean_time = dask.delayed(np.mean)(works)
    return mean_time.compute(scheduler='processes')

def main(min_processes, max_processes, step_processes):
    x, y = [], []
    for nb_processes in range(min_processes, max_processes, step_processes):
        print("Test with %d processes." % nb_processes)
        x.append(nb_processes)
        y.append(round(parallel_works(nb_processes), 2))
        print("  ==> %f" % y[-1])
    
    print(x)
    print(y)
    plt.plot(x, y)
    plt.show
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument("--min_processes", type=int, help="Max number of process to simultaneously start.")
    parser.add_argument("--max_processes", type=int, help="Max number of process to simultaneously start.")
    parser.add_argument("--step_processes", type=int, help="Step number of processes to increment.")
    args = parser.parse_args()

    main(args.min_processes, args.max_processes, args.step_processes)
