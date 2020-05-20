import os
import glob


def load_txt(fn):
    with open(fn) as fh:
        return [line.strip() for line in fh]


def dump_txt(content, fn):
    with open(fn, 'w') as fh:
        for line in content:
            fh.write("{}\n".format(line))


def main():
    new_files = glob.glob("/mnt/sdd1/Research/AdjTomo/source_inversion_II/events/global_cmt/quakeml#dur-16__mag5.8-7.2/*.xml")
    new_files = [os.path.basename(x) for x in new_files]
    cmt_events = [x.split('.')[0] for x in new_files]
    print("Total cmt events: {}".format(len(cmt_events)))

    events_inv = load_txt("/mnt/sdd1/Research/AdjTomo/source_inversion_II/events/used_events/eventlist.1480")
    events_hold = load_txt("/mnt/sdd1/Research/AdjTomo/source_inversion_II/events/used_events/eventlist.360")

    events_used = set(events_inv + events_hold)
    print("Total events used: {}".format(len(events_used)))

    new_events = [x for x in cmt_events if x not in events_used]
    print("New events: {}".format(len(new_events)))
    tmp = [x for x in cmt_events if x in events_used]
    print("events already used: {}".format(len(tmp)))

    new_events.sort()
    dump_txt(new_events, "new_events.txt")


if __name__ == "__main__":
    main()
