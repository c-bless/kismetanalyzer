#!/usr/bin/env python

# Simple script to export a list of access points to either csv and / or
# to kml.
#
# @author Christoph Bless
#
from __future__ import print_function

import argparse
import json
import sqlite3
import sys

from fastkml import kml, styles
from pygeoif import geometry

from kismetanalyzer.model import Device
from kismetanalyzer.util import does_ssid_matches


def get_description(dev):
    """
    This function is used to create the description string for the device.

    :param ap: instance of kismetanalzer.model.Device class

    :return: A string which can be used as description for the device
    :rtype string
    """
    desc = "MAC: {0}\nName: {1}\nCommonname: {2}\nPhyName: {3}\nManufacturer: {4}\nType: {5}\nFrequency: {6}\nChannel: {7}"
    description = desc.format(dev.mac, dev.name, dev.commonname, dev.phyname, dev.manufacturer, dev.type, dev.frequency, dev.channel)
    return description


def export_csv(filename, devices, delimiter=";"):
    """
    Export found devices to a CSV file. The filename prefix and the list
    of devices is required. The delimiter is optional.

    :param filename: Prefix for the filename. The extension "csv" will be added
    :param devices: list of devices. Each device must be a tuple with
                    the following format (lon, lat, mac, title, encryption, description )
    :param delimiter: Delimiter to use for separation of columns (optional)
    """
    import csv

    num_plotted = 0

    outfile = "{0}-devices.csv".format(filename)

    with open(outfile, mode='w') as csv_file:
        w = csv.writer(csv_file, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(['MAC-Address', 'TYPE', 'NAME', 'COMMONNAME', 'PHYNAME', 'Frequency', 'Channel', 'Manufacturer'])
        for dev in devices:
            w.writerow([dev.mac, dev.type, dev.name, dev.commonname, dev.phyname, dev.frequency, dev.channel, dev.manufacturer])
            num_plotted = num_plotted + 1

    print("Exported {} devices to {}".format(num_plotted, outfile))


def export_kml(filename, title, devices):
    """
    Export found devices to a KML file which can be imported to Googleearth.
    The filename prefix and the list of devices is required.

    :param filename: Prefix for the filename. The extension "kml" will be added
    :param title: name which will be added to kml file
    :param devices: list of devices. Each device must be a tuple in the following format (lon, lat, mac, title, encryption, description )
   """
    num_plotted = 0
    outfile = "{0}-devices.kml".format(filename)

    # create a KML file skeleton
    k = kml.KML()
    ns = '{http://www.opengis.net/kml/2.2}'

    doc = kml.Document(ns, "docid", title, '')
    k.append(doc)

    # create placemark for the access point, and add it to the KML document
    for dev in devices:
        icon_style = styles.IconStyle(ns=ns, color="ff00ffff")
        style = styles.Style(ns=ns, styles=[icon_style])
        desc = get_description(dev)
        p = kml.Placemark(name=dev.name, description=desc, styles=[style])
        p.geometry = geometry.Point(dev.location.lat, dev.location.lon, dev.location.alt)
        doc.append(p)
        num_plotted = num_plotted + 1

    with open(outfile, "w") as f:
        s = str(k.to_string(prettyprint=True))
        f.write(s)

    print("Exported {} devices to {}".format(num_plotted, outfile))


def gen_devlist():
    parser = argparse.ArgumentParser(description="List devices discovered by kismet.")
    parser.add_argument("--in", action="store", dest="infile", required=True, help='Input file (.kismet)')
    parser.add_argument("--out", action="store", dest="outfile", help='Output filename (optional)')
    parser.add_argument("--title", action="store", dest="title", default="Kismet", help='Title embedded in KML file')
    parser.add_argument("--csv", action="store_true", dest="csv", default=False, help="Export results to csv")
    parser.add_argument("--kml", action="store_true", dest="kml", default=False, help="Export results to kml")
    parser.add_argument("--strongest-point", action="store_true", dest="strongest", default=False,
                        help='Plot points based on strongest signal')
    parser.add_argument("--type", action="store", dest="type", default=None, help='Filter by Type')
    parser.add_argument("--verbose", action="store_true", dest="verbose", default=False,
                        help="Print MAC, TYPE, CHANNEL type to stdout")
    parameters = parser.parse_args()

    # set the filename prefix for the output file if it is not specified
    # via the parameter --out
    if parameters.outfile is None:
        if parameters.infile.endswith(".kismet"):
            parameters.outfile = parameters.infile[:-7]
        else:
            parameters.outfile = parameters.infile

    try:
        db = sqlite3.connect(parameters.infile)
    except Exception as e:
        print("Failed to open kismet logfile: {0}".format(e))
        sys.exit(1)

    try:
        sql = "SELECT * FROM devices; "
        c = db.cursor()
        sql_result = c.execute(sql)
    except:
        print("Failed to extract data from database")
        sys.exit()

    # container for collecting relevant devices
    devs = []
    for row in sql_result:
        try:
            # create a device dictionary from json string stored in the
            # device column of the kismet database
            dev = json.loads(row[14])
            # convert json device string into an instance of the
            # class kismetanalyzer.model.AccessPoint
            strongest = parameters.strongest
            d = Device.from_json(dev, strongest)
            if parameters.type is not None:
                if parameters.type not in d.type:
                    continue

            if parameters.verbose:
                print("{:20s}{:40s}{:10s}".format(d.mac, d.type, d.channel))

            devs.append(d)

        except Exception as e:
            continue

    if parameters.csv:
        export_csv(parameters.outfile, devs)

    if parameters.kml:
        export_kml(parameters.outfile, parameters.title, devs)
