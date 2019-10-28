import sys


def main():
    nb = 30000000

    a = list(range(nb))
    print(sys.getsizeof(a))
    for i in a:
        i = i + 1
    for i in range(nb):
        a.pop()


if __name__ == "__main__":
    main()
