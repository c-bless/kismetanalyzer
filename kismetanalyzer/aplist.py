#!/usr/bin/env python

# Simple script to export a list of access points to either csv and / or 
# to kml.
#
# @author Christoph Bless
# 


import argparse
import json
import sqlite3
import sys
import simplekml
from kismetanalyzer.model import AccessPoint
from kismetanalyzer.util import does_ssid_matches


def get_description(dev):
    """
    This fuction is used to creat the description string for the device.
    
    :param dev: json string from the kismet database column "device"
    
    :return: A string which can be used as description for the device
    :rtype string
    """
    desc = "Encryption: {0}\nFrequency: {1}\nChannel: {2}\nManufacturer: {3}"
    #description = desc.format(ka_parser.parse_encryption(dev),
    #                        ka_parser.parse_frequency(dev),
    #                        ka_parser.parse_channel(dev),
    #                        ka_parser.parse_manufacturer(dev))
    return desc
    
    
def get_networkcolor(encryption):
    """
    This fuction is used to get color for a network which will be added 
    to a KML-File.
    
    :param encryption: encryption string 
    
    :return: Color to use for the network
    :rtype simplekml.Color
    """
    if 'WPA' in encryption:
        return simplekml.Color.green
    elif 'WEP' in encryption:
        return simplekml.Color.orange
    elif 'Open' in encryption: 
        return simplekml.Color.red
    else: 
        return simplekml.Color.yellow


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
        
    print "Exported {} devices to {}".format(num_plotted, outfile)
        
        
def export_kml(filename, title, devices):
    """
    Export found devices to a KML file which can be imported to Googleearth. 
    The filename prefix and the list of devices is required. 
    
    :param filename: Prefix for the filename. The extention "kml" will be added
    :param devices: list of devices. Each device must be a tuple with 
                    the followin format (lon, lat, mac, title, encryption, description )
    """
    num_plotted = 0
    outfile = "{0}.kml".format(filename)
    
    kml = simplekml.Kml()
    kml.document.name = title
        
    for dev in devices:
        pt = kml.newpoint(name = dev.ssid)
        pt.coords = [(dev.location.lon, dev.location.lat, dev.location.alt)]
        icon_color = get_networkcolor(dev.encryption)
        pt.style.iconstyle.color = icon_color
        pt.description = dev.encryption
        num_plotted = num_plotted + 1
        
    kml.save(outfile)
    print "Exported {} devices to {}".format(num_plotted, outfile)


def gen_aplist():
    parser = argparse.ArgumentParser(description="Kismet to KML Log Converter")
    parser.add_argument("--in", action="store", dest="infile", required=True, help='Input (.kismet) file')
    parser.add_argument("--out", action="store", dest="outfile", help='Output filename (optional)')
    parser.add_argument("--title", action="store", dest="title", default="Kismet", help='Title embedded in KML file')
    parser.add_argument("--ssid", action="store", dest="ssid", help='Only plot networks which match the SSID (or SSID regex)')
    parser.add_argument("--exclude-ssid", action="store", dest="excludessid", help='Only plot networks which match the SSID (or SSID regex)')
    parser.add_argument("--strongest-point", action="store_true", dest="strongest", default=False, help='Plot points based on strongest signal')
    parser.add_argument("--encryption", action="store", dest="encryption", default=None, help="show only networks with given encryption type" )
    parser.add_argument("--csv", action="store_true", dest="csv", default=False, help="export results to csv")
    parser.add_argument("--kml", action="store_true", dest="kml", default=False, help="export results to kml")
    
    parameters = parser.parse_args()

    # set the filename prefix for the output file  if it not specified 
    # via the parameter --out
    if parameters.outfile is None:
        if parameters.infile.endswith(".kismet"):
            parameters.outfile = parameters.infile[:-7]
        else:
            parameters.outfile = parameters.infile
    
    try:
        db = sqlite3.connect(parameters.infile)
    except Exception as e:
        print "Failed to open kismet logfile: ", e
        sys.exit(1)
    
    try:  
        sql = "SELECT * FROM devices where type='Wi-Fi AP'; "
        c = db.cursor()
        sql_result = c.execute(sql)    
    except:
        print "Failed to extract data from database"
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
            print "main2"
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
                if does_ssid_matches(dev, parameters.ssid):
                    # SSID matches, skip this access point
                    continue
            
            # skip device if the secified encryption string is not 
            # present in the device encryption string
            if parameters.encryption:
                if not parameters.encryption in ap.encryption:
                    continue
                    
            devs.append(ap)
        
        except Exception as e:
            continue

    
    if parameters.csv:
        export_csv(parameters.outfile, devs)
         
    if parameters.kml:
        export_kml(parameters.outfile, parameters.title, devs)