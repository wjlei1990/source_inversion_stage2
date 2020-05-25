import os
import glob
import numpy as np
import obspy
import json


def dump_json(content, fn):
    with open(fn, 'w') as fh:
        json.dump(content, fh, indent=2, sort_keys=True)


def load_txt(fn):
    with open(fn) as fh:
        return [line.strip() for line in fh]


def main():
    #eventfile = "../new_events.txt"
    #inputdir = "../../global_cmt.2005-recent/quakeml#dur-16__mag5.8-7.2/"
    #fmt="QuakeML"
    #outputfn = "events.1738.json"

    #eventfile = "../../used_events/eventlist.1480"
    #inputdir = "../../used_events/CMT.inversion"
    #fmt="CMTSOLUTION"
    #outputfn = "events.1480.json"

    eventfile = "../../used_events/eventlist.360"
    inputdir = "../../used_events/CMT.held-out"
    fmt="CMTSOLUTION"
    outputfn = "events.360.json"

    events = load_txt(eventfile)
    print("Number of events: {}".format(len(events)))

    depth_threshold = 300
    ndeep = 0

    results = {}
    for eventname in events:
        if fmt == "QuakeML":
            fn = os.path.join(inputdir, "{}.xml".format(eventname))
        else:
            fn = os.path.join(inputdir, eventname)

        event = obspy.read_events(fn, format=fmt)[0]

        origin = event.preferred_origin()
        info = {
            "time": "{}".format(origin.time),
            "latitude": origin.latitude,
            "longitude": origin.longitude,
            "depth_in_m": origin.depth,
        }
        results[eventname] = info
        depth_in_km = origin.depth / 1000.0
        if depth_in_km > depth_threshold:
            ndeep += 1

    print("Events depth > {}km: {}".format(depth_threshold, ndeep))

    dump_json(results, outputfn)



if __name__ == "__main__":
    main()
