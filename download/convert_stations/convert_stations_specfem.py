import yaml
import time
import glob
import os
import json
from pprint import pprint
from pytomo3d.station.utils import write_stations_file


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print("%r  %2.2f s" % (method.__name__, (te - ts)))
        return result
    return timed


def safe_mkdir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def load_yaml(fn):
    with open(fn) as fh:
        return yaml.load(fh, Loader=yaml.FullLoader)


def load_txt(fn):
    with open(fn) as fh:
        return [line.strip() for line in fh]


def load_json(fn):
    with open(fn) as fh:
        return json.load(fh)


def dump_json(content, fn):
    with open(fn, 'w') as fh:
        json.dump(content, fh, indent=2, sort_keys=True)


def validate_station(stations):
    true_values =  {
        # nw.sta: [latitude, longitude, elevation(m), burial(m)]
        "II.AAK": [42.6375, 74.4942, 1633.1, 30.0],
        "II.ABKT": [37.9304, 58.1189, 678, 7.0]
    }

    isGood = True
    n = 0
    for tag in true_values:
        if tag not in stations:
            continue
        if stations[tag] != true_values[tag]:
            isGood = False
            print("Failed to pass AAK data validation: {} vs {}".format(
                stations[tag], true_values[tag]
            ))
        else:
            n += 1

    if not isGood:
        raise ValueError("Failed to pass the station validation test")
    else:
        print("Pass the Validation test [{}/{}]".format(n, len(true_values)))


@timeit
def convert_one_event(inputfile, outputfn):
    info = load_json(inputfile)
    print("Number of channels: {}".format(len(info)))

    channels = list(info.keys())
    channels.sort()

    results = {}
    for channel in channels:
        _nw, _sta, _loc, _chan = channel.split(".")
        tag = "{}.{}".format(_nw, _sta)
        _data = info[channel]
        if tag in results:
            continue
        results[tag] = [
            _data["latitude"],
            _data["longitude"],
            _data["elevation"],
            _data["depth"]]

    print("Number of stations: ", len(results))
    validate_station(results)
    write_stations_file(results, outputfn)


def f(data):
    print("[{}] {}".format(os.getpid(), len(data)))


@timeit
def convert_specfem_station(eventlist, json_base, output_base):
    for i, eventname in enumerate(eventlist):
        print("=============> [{} / {}] {}".format(
            i+1, len(eventlist), eventname))
        inputfile = os.path.join(
                json_base, "STATIONS.{}.json".format(eventname))
        outputfn = os.path.join(
                output_base, "STATIONS.{}".format(eventname))
        print("inputfile: {}".format(inputfile))
        print("outputfn: {}".format(outputfn))
        convert_one_event(inputfile, outputfn)


def main():
    json_base = "/tigress/lei/source_inversion_II/download.1480/station.json"
    output_base = "/tigress/lei/source_inversion_II/download.1480/station.specfem"
    eventfile = "./eventlist.440"

    events = load_txt(eventfile)
    print("Number of events: {}".format(len(events)))

    safe_mkdir(output_base)
    convert_specfem_station(events, json_base, output_base)


if __name__ == "__main__":
    main()
