from kismetanalyzer.model import AccessPoint
from kismetanalyzer.util import json_to_accesspoint

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
        sql = "SELECT * FROM devices where type='Wi-Fi AP';"
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

            ap 
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
            
            # extract location data for the access point
            lon, lat, alt = ka_parser.parse_loc(dev, parameters.strongest)
            
            # extract the encryption type the wireless network from the 
            # device dictionary
            encryption = ka_parser.parse_encryption(dev)
            
            # skip device if the secified encryption string is not 
            # present in the device encryption string
            if parameters.encryption:
                if not parameters.encryption in encryption:
                    continue
                    
            # extract MAC-Address, network name, and description 
            mac = ka_parser.parse_mac(dev)
            networkname = ka_parser.parse_networkname(dev)
            
            device = (lon, lat, alt, mac, networkname, encryption, description )
            devs.append(device)
        
        except Exception as e:
            continue

    print len(devs)
    
    if parameters.csv:
        export_csv(parameters.outfile, devs)