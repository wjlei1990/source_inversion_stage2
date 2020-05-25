import numpy as np
import json
import obspy
import os
import glob


def load_json(fn):
    with open(fn) as fh:
        return json.load(fh)


def dump_json(content, fn):
    with open(fn, 'w') as fh:
        json.dump(content, fh, indent=2, sort_keys=True)


def dump_txt(content, fn):
    with open(fn, 'w') as fh:
        for line in content:
            fh.write("{}\n".format(line))


def load_events():
    events_new = load_json("./events.1738.json")
    print("Number of new events: {}".format(len(events_new)))

    events_1 = load_json("./events.1480.json")
    events_2 = load_json("./events.360.json")
    events_1.update(events_2)
    print("Number of old events: {}".format(len(events_1)))

    return events_new, events_1


def filter_depth(events_new, threshold):
    results = {}
    for ev in events_new:
        depth_in_km = events_new[ev]["depth_in_m"] / 1000.0
        if depth_in_km >= threshold:
            results[ev] = events_new[ev]

    for k in results:
        events_new.pop(k)

    return results


def calculate_weights(event, events_old, delta):
    lat1 = event["latitude"]
    lon1 = event["longitude"]

    dists = []
    for ev in events_old:
        lat2 = events_old[ev]["latitude"]
        lon2 = events_old[ev]["longitude"]
        d = obspy.geodetics.locations2degrees(lat1, lon1, lat2, lon2)
        dists.append(d)

    dists = np.array(dists)
    weight = 1.0 / np.sum(np.exp(-(dists/delta)**2))
    return weight


def inbox(lat, lon, bl, tr):
    if bl[0] <= lat and lat <= tr[0] and bl[1] <= lon and lon <= tr[1]:
        return True
    return False


def modify_weights_on_region(events, weights):
    return weights

    for ev in events:
        lat = events[ev]["latitude"]
        lon = events[ev]["longitude"]
        if inbox(lat, lon, [-20, 90], [20, 120]):
            weights[ev] *= 0.1
        if inbox(lat, lon, [-50, 120], [50, 180]):
            weights[ev] *= 0.1


def select_on_distance(events_new, events_old, delta):
    weights = {}
    ntotal = len(events_new)
    for i, ev in enumerate(events_new):
        if i % int(ntotal / 20) == 0:
            print("Calculating weights {}/{} {:.1f}%".format(
                i+1, ntotal, (i+1)/ntotal*100.0))
        w = calculate_weights(events_new[ev], events_old, delta)
        weights[ev] = w
        #if i > 100:
        #    break

    return weights


def main():
    events_new, events_old = load_events()

    # first get the deep events in the new events
    th = 150
    deep_new_events = filter_depth(events_new, th)
    print("deep and rest events: {}, {}".format(
        len(deep_new_events), len(events_new)))
    outputfn = "eventlist_1738.depth_{}km".format(th)
    print("deep events(>{}km) saved to: {}".format(th, outputfn))
    dump_txt([k for k in deep_new_events], outputfn)
    return

    delta = 2.0
    weights = select_on_distance(events_new, events_old, delta)

    outputfn = "eventlist_1738__delta{:.1f}__weights.json".format(delta)
    print("event weights saved to: {}".format(outputfn))
    dump_json(weights, outputfn)

    # sort weights
    _weights = [(v, k) for k, v in weights.items()]
    _weights.sort(reverse=True)
    print("Events with max and min weights: {}({:.2e}), {}({:.2e})".format(
        _weights[0][1], _weights[0][0], _weights[-1][1], _weights[-1][0]
    ))


if __name__ == "__main__":
    main()
