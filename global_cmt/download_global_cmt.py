import os
import requests
import time


def download_from_url(url, fn):
    r = requests.get(url, timeout=2.0)

    if r.status_code != requests.codes.ok:
        print("Failed to download: ", r.status_code)
        return

    with open(fn, 'wb') as fh:
        fh.write(r.content)

    time.sleep(1)


def download_one_ndk(year, month, outputdir):
    base_url = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/NEW_MONTHLY/"
    year_str = "{}".format(year)
    tag = "{}{}.ndk".format(month, year_str[2:])
    url = base_url + "{}/{}".format(year, tag)

    fn = os.path.join(outputdir, tag)
    print("url: ", url)
    print("fn: ", fn)
    download_from_url(url, fn)


def safe_mkdir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def main():

    #years = [i for i in range(2005, 2020)]
    years = [i for i in range(2005, 2020)]
    #months = ["jan", "feb", "mar", "apr", "may", "june",
    #          "july", "aug", "sept", "oct", "nov", "dec"]
    months = ["jun", "jul", "sep"]
    for year in years:
        outputdir = os.path.join("ndk", "{}".format(year))
        safe_mkdir(outputdir)
        for month in months:
            print("=======> {} {}".format(year, month))
            download_one_ndk(year, month, outputdir)


if __name__ == "__main__":
    main()
