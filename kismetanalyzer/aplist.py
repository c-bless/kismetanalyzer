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

from kismetanalyzer.model import AccessPoint
from kismetanalyzer.util import does_ssid_matches


def get_description(ap):
    """
    This fuction is used to create the description string for the device.
    
    :param ap: instance of kismetanalzer.model.AccessPoint class
    
    :return: A string which can be used as description for the device
    :rtype string
    """
    clients = "\n".join(ap.client_map)
    desc = "MAC: {0}\nEncryption: {1}\nFrequency: {2}\nChannel: {3}\nManufacturer: {4}\n\nClients:\n{5}"
    description = desc.format(ap.mac, ap.encryption, ap.frequency, ap.channel, ap.manufacturer, clients)
    return description
    
    
def get_networkcolor(encryption):
    """
    This fuction is used to get color for a network which will be added 
    to a KML-File.s
    
    :param encryption: encryption string 
    
    :return: Color to use for the network
    :rtype simplekml.Color
    """
    if 'WPA' in encryption:
        # green
        return "ff008000"
    elif 'WEP' in encryption:
        # orange
        return "ff00a5ff"
    elif 'Open' in encryption: 
        # red
        return "ff0000ff"
    else:
        # yellow
        return "ff00ffff"


def export_csv(filename, devices, delimiter=";"):
    """
    Export found devices to a CSV file. The filename prefix and the list 
    of devices is required. The delimiter is optional.
    
    :param filename: Prefix for the filename. The extention "csv" will be added
    :param devices: list of devices. Each device must be a tuple with 
                    the followin format (lon, lat, mac, title, encryption, description )
    :param delimiter: Delimiter to use for separation of columns (optional)
    """
    import csv
    
    num_plotted = 0
    
    outfile = "{0}.csv".format(filename)
    
    with open(outfile, mode='w') as csv_file:
        w = csv.writer(csv_file, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(['MAC-Address', 'SSID', 'Encryption'])
        for dev in devices:
            w.writerow([dev.mac, dev.ssid, dev.encryption])
            num_plotted = num_plotted + 1
        
    print ("Exported {} devices to {}".format(num_plotted, outfile))


def export_kml(filename, title, devices):
    """
    Export found devices to a KML file which can be imported to Googleearth.
    The filename prefix and the list of devices is required.

    :param filename: Prefix for the filename. The extention "kml" will be added
    :param title: name which will be added to kml file
    :param devices: list of devices. Each device must be a tuple in the following format (lon, lat, mac, title, encryption, description )
   """
    num_plotted = 0
    outfile = "{0}.kml".format(filename)

    # create a KML file skeleton
    k = kml.KML()
    ns = '{http://www.opengis.net/kml/2.2}'

    doc = kml.Document(ns, "docid", title, '')
    k.append(doc)

    # create placemark for the access point, and add it to the KML document
    for dev in devices:
        icon_style = styles.IconStyle(ns=ns, color=get_networkcolor(dev.encryption))
        style = styles.Style(ns=ns, styles=[icon_style])
        desc = get_description(dev)
        p = kml.Placemark(name=dev.ssid, description=desc, styles=[style])
        p.geometry = geometry.Point(dev.location.lon, dev.location.lat, dev.location.alt)
        doc.append(p)
        num_plotted = num_plotted + 1

    with open (outfile, "w") as f:
        s = str(k.to_string(prettyprint=True))
        f.write(s)

    print("Exported {} devices to {}".format(num_plotted, outfile))


def gen_aplist():
    parser = argparse.ArgumentParser(description="List access points discovered by kismet.")
    parser.add_argument("--in", action="store", dest="infile", required=True, help='Input file (.kismet)')
    parser.add_argument("--out", action="store", dest="outfile", help='Output filename (optional)')
    parser.add_argument("--title", action="store", dest="title", default="Kismet", help='Title embedded in KML file')
    parser.add_argument("--ssid", action="store", dest="ssid", help='Only plot networks which match the SSID (or SSID regex)')
    parser.add_argument("--exclude-ssid", action="store", dest="excludessid", help='Exclude networks which match the SSID (or SSID regex)')
    parser.add_argument("--strongest-point", action="store_true", dest="strongest", default=False, help='Plot points based on strongest signal')
    parser.add_argument("--encryption", action="store", dest="encryption", default=None, help="Show only networks with given encryption type" )
    parser.add_argument("--csv", action="store_true", dest="csv", default=False, help="Export results to csv")
    parser.add_argument("--kml", action="store_true", dest="kml", default=False, help="Export results to kml")
    parser.add_argument("--verbose", action="store_true", dest="verbose", default=False, help="Print MAC, SSID, encryption type to stdout")
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
    devs = []
    
    for row in sql_result:
        try:
            # create a device dictionary from json string stored in the
            # device column of the kismet database
            dev = json.loads(row[14])
            
            # convert json device string into an instance of the 
            # class kismetanalyzer.model.AccessPoint
            strongest = parameters.strongest
            ap = AccessPoint.from_json(dev, strongest)
            # Apply SSID filter if it is used as parameter (this switch
            # checks the included SSID list, which is provided by the 
            # parameter --ssid 
            if parameters.ssid is not None:
                if not does_ssid_matches(dev, parameters.ssid):
                    # SSID doesn't match, skip this access point
                    continue
            
            # Apply SSID filter if it is used as parameter (this switch 
            # checks the excluded SSID list, which is provided by the 
            # parameter --exclude-ssid )
            if parameters.excludessid is not None:
                if does_ssid_matches(dev, parameters.excludessid):
                    # SSID matches, skip this access point
                    continue
            
            # skip device if the secified encryption string is not 
            # present in the device encryption string
            if parameters.encryption:
                if not parameters.encryption in ap.encryption:
                    continue


            if parameters.verbose:
                print ("{:20s}{:20s}{:40s}".format(ap.mac, ap.encryption, ap.ssid))

            devs.append(ap)
        
        except Exception as e:
            continue

    
    if parameters.csv:
        export_csv(parameters.outfile, devs)
         
    if parameters.kml:
        export_kml(parameters.outfile, parameters.title, devs)
