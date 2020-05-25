import json


def load_json(fn):
    with open(fn) as fh:
        return json.load(fh)


def dump_txt(content, fn):
    with open(fn, 'w') as fh:
        for line in content:
            fh.write("{}\n".format(line))


def inbox(lat, lon, bl, tr):
    if bl[0] <= lat and lat <= tr[0] and bl[1] <= lon and lon <= tr[1]:
        return True
    return False


def modify_weights_on_region(events, weights):
    print("modify weights on region...")
    for ev in weights:
        lat = events[ev]["latitude"]
        lon = events[ev]["longitude"]
        if inbox(lat, lon, [-20, 90], [20, 120]):
            # asia
            weights[ev] *= 0.25
        if inbox(lat, lon, [-50, 120], [65, 180]):
            # asia and Fiji
            weights[ev] *= 0.25
        if inbox(lat, lon, [-10, -90], [30, -60]):
            # central and south america
            weights[ev] *= 0.15


def main():
    weights = load_json("eventlist_1738__delta2.0__weights.json")
    print("Number of events: {}".format(len(weights)))

    events = load_json("events.1738.json")

    modify_weights_on_region(events, weights)

    ws = [(v, k) for k, v in weights.items()]
    ws.sort(reverse=True)
    events = [x[1] for x in ws]
    dump_txt(events, "eventlist_1738__deta2.0.weights_order")


if __name__ == "__main__":
    main()
