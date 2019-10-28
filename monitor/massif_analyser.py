import argparse
from matplotlib import pyplot as plt
import numpy as np

def main(filepath):
    with open(filepath, 'r') as file:
        data = file.read()
    lines = data.split("\n")
    time_lines = np.array([int(''.join(filter(str.isdigit, line))) for line in lines if "time=" in line])
    mem_heap_B_lines = np.array([int(''.join(filter(str.isdigit, line))) for line in lines if "mem_heap_B=" in line])
    # mem_heap_extra_B_lines = np.array([int(''.join(filter(str.isdigit, line)))for line in lines if "mem_heap_extra_B=" in line])

    print("Maximum Memory usage : %02f MB" % (np.max(mem_heap_B_lines)/1000000.0))
    print("Mean Memory usage : %02f MB" % (np.mean(mem_heap_B_lines)/1000000.0))

    # print(max(mem_heap_B_lines + mem_heap_extra_B_lines))
    plt.plot(time_lines, mem_heap_B_lines/1000000.0)
    plt.xlabel("Time (ms)")
    plt.ylabel("Memory utilization (MB)")
    plt.show()
    # print(time_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        "filepath", type=str, help="Filepath of the massif.out.xxxxx"
    )
    args = parser.parse_args()

    main(args.filepath)