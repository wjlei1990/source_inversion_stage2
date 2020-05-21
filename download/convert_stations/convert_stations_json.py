import yaml
import time
import glob
import os
import json
from pprint import pprint
from multiprocessing import Process
from pytomo3d.station.extract_staxml_info import extract_staxml_info
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


def dump_json(content, fn):
    with open(fn, 'w') as fh:
        json.dump(content, fh, indent=2, sort_keys=True)


@timeit
def convert_one_event(input_dir, outputfn):
    files = glob.glob(os.path.join(input_dir, "*.xml"))
    print("Number of files in directory: {}".format(len(files)))

    info = {}
    for i, fn in enumerate(files):
        #print("{}/{}".format(i+1, len(files)))
        info.update(extract_staxml_info(fn))

    print("Number of channels: {}".format(len(info)))

    fn = outputfn
    dump_json(info, fn)


def f(data):
    print("[{}] {}".format(os.getpid(), len(data)))


@timeit
def serial_convert(eventlist, stationxml_base, output_base):
    for i, eventname in enumerate(eventlist):
        print("=============> [{} / {}] {}".format(
            i+1, len(eventlist), eventname))
        input_dir = os.path.join(stationxml_base, eventname)
        outputfn = os.path.join(
                output_base, "STATIONS.{}.json".format(eventname))
        print("input_dir: {}".format(input_dir))
        print("output fn: {}".format(outputfn))
        convert_one_event(input_dir, outputfn)


@timeit
def parallel_convert(eventlist, stationxml_base, output_base, nproc=1):
    print("Total number of events: {}".format(len(eventlist)))

    proc_list = []
    for iproc in range(nproc):
        proc_events = eventlist[iproc::nproc]
        #p = Process(target=f, args=(proc_events,))
        p = Process(
            target=serial_convert,
            args=(proc_events, stationxml_base, output_base)
        )
        p.start()
        proc_list.append(p)

    for p in proc_list:
        p.join()


def main():
    basedir = "/gpfs/alpine/geo111/proj-shared/wenjie/source_inversion_II/data/download"
    stationxml_base = os.path.join(basedir, "station")
    output_base = os.path.join(basedir, "station.json")
    eventfile = "./eventlist.738"

    events = load_txt(eventfile)
    print("Number of events: {}".format(len(events)))

    safe_mkdir(output_base)
    serial_convert(events, stationxml_base, output_base)
    #parallel_download(events[:4], nproc=2)


if __name__ == "__main__":
    main()
