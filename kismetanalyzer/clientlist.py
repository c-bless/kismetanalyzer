#!/usr/bin/env python

# Simple script to export a list of connected clients for the given SSID.
#
# @author Christoph Bless
#
from __future__ import print_function

import argparse
import json
import sqlite3
import sys

from kismetanalyzer.model import AccessPoint
from kismetanalyzer.util import does_ssid_matches


def gen_clientlist():
    parser = argparse.ArgumentParser(description="Print a list of connected clients for the given SSID.")
    parser.add_argument("--in", action="store", dest="infile", required=True, help='Input file (.kismet)')
    parser.add_argument("--ssid", action="store", dest="ssid", required=True,
                        help='SSID (or SSID regex)')
    parameters = parser.parse_args()


    try:
        db = sqlite3.connect(parameters.infile)
    except Exception as e:
        print ("Failed to open kismet logfile: {0}".format(e))
        sys.exit(1)

    try:
        sql = "SELECT * FROM devices where type='Wi-Fi AP'; "
        c = db.cursor()
        sql_result = c.execute(sql)
    except:
        print ("Failed to extract data from database")
        sys.exit()

    # container for collecting relevant devices
    devs = set()

    for row in sql_result:
        try:
            # create a device dictionary from json string stored in the
            # device column of the kismet database
            dev = json.loads(row[14])

            # convert json device string into an instance of the
            # class kismetanalyzer.model.AccessPoint
            ap = AccessPoint.from_json(dev)

            # Apply SSID filter if it is used as parameter (this switch
            # checks the included SSID list, which is provided by the
            # parameter --ssid
            if parameters.ssid is not None:
                if not does_ssid_matches(dev, parameters.ssid):
                    # SSID doesn't match, skip this access point
                    continue

            client_map = ap.client_map
            for c in client_map:
                devs.add(c)

        except Exception as e:
            continue

    print("\n".join(devs))
