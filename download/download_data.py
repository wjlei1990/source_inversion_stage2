import yaml
import time
import os
from pprint import pprint
import obspy
from obspy.clients.fdsn.mass_downloader import RectangularDomain, \
        Restrictions, MassDownloader
from multiprocessing import Process


waveform_base = "/tigress/lei/source_inversion_II/download/waveform"
station_base = "/tigress/lei/source_inversion_II/download/station"


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


def get_event_time(event):
    origin = event.preferred_origin()
    return origin.time


def download_data(starttime, endtime, waveform_dir, station_dir,
                  networks=None, channels=None, providers=None,
                  minimum_length=0.95):
    # Rectangular domain containing parts of southern Germany.
    domain = RectangularDomain(
        minlatitude=-90, maxlatitude=90,
        minlongitude=-180, maxlongitude=180)

    if isinstance(channels, list):
        channels = ",".join(channels)

    if isinstance(networks, list):
        networks = ",".join(networks)

    # Set download restrictions
    restrictions = Restrictions(
        starttime=starttime, endtime=endtime,
        reject_channels_with_gaps=False,
        minimum_length=minimum_length,
        network=networks, channel=channels,
        location_priorities=["", "00", "10"]
    )

    if providers is None:
        mdl = MassDownloader()
    else:
        mdl = MassDownloader(providers=providers)

    mdl.download(domain, restrictions,
                 mseed_storage=waveform_dir,
                 stationxml_storage=station_dir)


def download_event(eventname, event, params):
    # Request config_file
    event_time = get_event_time(event)

    obsd_dir = os.path.join(waveform_base, eventname)
    safe_mkdir(obsd_dir)
    station_dir = os.path.join(station_base, eventname)
    safe_mkdir(station_dir)

    starttime = event_time + params["starttime_offset"]
    endtime = event_time + params["endtime_offset"]
    print(event_time)
    print(starttime, endtime)

    # Get station_list from station_file in database entry
    download_data(starttime, endtime, obsd_dir, station_dir,
                  networks=params["networks"],
                  channels=params["channels"],
                  providers=params["providers"])


def download_eventlist(eventlist):
    quakeml_dir = "./quakeml#dur-16__mag5.8-7.2"
    print("[pid={}] nevents={}".format(os.getpid(), len(eventlist)))

    time.sleep(2)
    params = load_yaml("./params.yml")
    pprint(params)

    for ie, eventname in enumerate(eventlist):
        fn = os.path.join(quakeml_dir, "{}.xml".format(eventname))
        event = obspy.read_events(fn, format="quakeml")[0]
        try:
            download_event(eventname, event, params)
        except Exception as exp:
            print("Error downloading event {}: {}".format(
                eventname, exp))


@timeit
def serial_download(eventlist):
    download_eventlist(eventlist)


def f(data):
    print("[{}] {}".format(os.getpid(), len(data)))


@timeit
def parallel_download(eventlist, nproc=1):
    print("Total number of events: {}".format(len(eventlist)))

    proc_list = []
    for iproc in range(nproc):
        proc_events = eventlist[iproc::nproc]
        #p = Process(target=f, args=(proc_events,))
        p = Process(target=download_eventlist, args=(proc_events,))
        p.start()
        proc_list.append(p)

    for p in proc_list:
        p.join()


def main():
    events = load_txt("./new_events.1000.txt")
    print("Number of events: {}".format(len(events)))

    safe_mkdir(waveform_base)
    safe_mkdir(station_base)

    serial_download(events)
    #parallel_download(events[:4], nproc=2)


if __name__ == "__main__":
    main()
