import os
import obspy
import glob
import logging


max_dur = 16
min_mag = 5.8
max_mag = 7.2


FORMAT='%(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)


def safe_mkdir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def get_magnitude(event):
    mag = event.preferred_magnitude()
    if mag.magnitude_type == 'Mwc':
        return mag.mag, mag.magnitude_type

    for mag in event.magnitudes:
        mtype = mag.magnitude_type
        if mtype.startswith("Mw"):
            return mag.mag, mag.magnitude_type

    # if not Mw not found, just return preferred_magnitude
    mag = event.preferred_magnitude()
    return mag.mag, mag.magnitude_type


def get_eventname(event):
    descs = event.event_descriptions

    eventname = None
    for desc in descs:
        if desc.type == "earthquake name":
            eventname = desc.text
    return eventname


def filter_ndk(fn, outputdir):
    events = obspy.read_events(fn, format="ndk")
    ntotal = len(events)

    no_mwc = 0
    ngood = 0
    for event in events:
        focal = event.preferred_focal_mechanism()
        dur = focal.moment_tensor.source_time_function.duration

        mag, mag_type = get_magnitude(event)
        if mag_type != "Mwc":
            log.debug("no Mwc:", mag_type)
            no_mwc += 1
            continue

        if dur > max_dur:
            continue

        if mag > max_mag or mag < min_mag:
            continue

        eventname = get_eventname(event)
        if eventname is None:
            raise ValueError("Failed to extract eventname: {}".format(
                event.event_descriptions
            ))

        log.debug("{}: duration={:<5.1f}, mag={:<5.2f}".format(
            eventname, dur, mag))
        outputfn = os.path.join(outputdir, "{}.xml".format(eventname))
        event.write(outputfn, format="quakeml")
        ngood += 1

    log.info("Number of events has no Mwc: {}".format(no_mwc))
    log.info("Number of good events: {} / {}".format(ngood, ntotal))


def main():
    years = [i for i in range(2005, 2020)]
    #years = [i for i in range(2018, 2020)]

    outputdir = "quakeml#dur-{:d}__mag{:.1f}-{:.1f}".format(
        max_dur, min_mag, max_mag)
    print("outputdir: {}".format(outputdir))
    safe_mkdir(outputdir)

    for year in years:
        print("=" * 20 + "> year: {}".format(year))
        pattern = os.path.join("ndk", "{}".format(year), "*.ndk")

        files = glob.glob(pattern)
        print("Number of files: {}".format(len(files)))

        for fn in files:
            print('-' * 10 + "file: {}".format(fn))
            filter_ndk(fn, outputdir)


if __name__ == "__main__":
    main()
