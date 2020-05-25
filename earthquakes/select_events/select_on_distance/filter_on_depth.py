import os
import json
import matplotlib.pyplot as plt
import sys


def load_json(fn):
    with open(fn) as fh:
        return json.load(fh)


def main():
    fn = sys.argv[1]
    events = load_json(fn)
    print("Number of events: {}".format(len(events)))

    depths = [events[x]["depth_in_m"] / 1000.0 for x in events]

    th = 100
    _tmp = [x for x in depths if x > th]
    print("Number of events deep than {}km: {}".format(th, len(_tmp)))

    th = 150
    _tmp = [x for x in depths if x > th]
    print("Number of events deep than {}km: {}".format(th, len(_tmp)))

    th = 300
    _tmp = [x for x in depths if x > th]
    print("Number of events deep than {}km: {}".format(th, len(_tmp)))

    plt.hist(depths, bins=20)
    plt.show()


if __name__ == "__main__":
    main()
