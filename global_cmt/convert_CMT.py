import glob
import os
import obspy


def main():
    files = glob.glob("quakeml#dur-16__mag5.8-7.2/*.xml")
    print("Number of quakeml files: {}".format(len(files)))

    outputdir = "cmt"

    for fn in files:
        print("====================")
        event = obspy.read_events(fn, format="quakeml")
        eventname = os.path.basename(fn).split(".")[0]
        print(fn)
        print(eventname)
        outputfn = os.path.join(outputdir, eventname)
        print(outputfn)
        event.write(outputfn, format="CMTSOLUTION")


if __name__ == "__main__":
    main()
