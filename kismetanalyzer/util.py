
# This script contains some functions to parse the json strings form the 
# kismet database column "device" of table "devices"

import re


def parse_clientmap(dev):
    clients = []
    if 'dot11.device' in dev:
        if "dot11.device.associated_client_map" in dev['dot11.device']:
            temp = dev['dot11.device']["dot11.device.associated_client_map"]
            for k in temp:
                # the key contains the client MAC address. only this is added to the client list
                clients.append(k)
    return clients


def parse_networkname(dev):
    """
    This fuction is used to parse the network name (SSID) from the json 
    string, which is written to the device column of the kismet database.
    
    :param dev: json string from the kismet database column "device"
    
    :return: A string either with the network name or MAC-Address if the SSID is not available
    :rtype string
    """
    netname = ""

    if 'kismet.device.base.name' in dev:
        netname = dev['kismet.device.base.name']

    if netname == "":
        if 'dot11.device' in dev:
            if 'dot11.device.last_beaconed_ssid' in dev['dot11.device']:
                netname = dev['dot11.device']['dot11.device.last_beaconed_ssid']

    if netname == "":
        netname = dev['kismet.device.base.macaddr']
    
    return netname
    

def parse_loc(dev, strongest=False):
    """
    This fuction is used to extract the longitude and latitude from a
    result set of an SQL query of the kismet database table devices. 
    
    :param row: SQL result set 
    
    :return: A tuple with longitude, latitude, altitude (long, lat, alt)
    :rtype tuple
    """
    loc = None
    lon = "0" 
    lat = "0"
    alt = "0"
    if 'kismet.device.base.location' in dev:
        if strongest:
            # strongest location
            if 'kismet.common.location.max_loc' in dev['kismet.device.base.location']:
                loc = dev['kismet.device.base.location']['kismet.common.location.max_loc']
                lon = loc['kismet.common.location.lon']
                lat = loc['kismet.common.location.lat']
                alt = loc['kismet.common.location.alt']
        else:
            # average location
            if 'kismet.common.location.avg_loc' in dev['kismet.device.base.location']:
                loc =  dev['kismet.device.base.location']['kismet.common.location.avg_loc']
                lon = loc['kismet.common.location.lon']
                lat = loc['kismet.common.location.lat']
                alt = loc['kismet.common.location.alt']
    
    return (lon, lat, alt)
    
def parse_mac(dev):
    """
    This fuction is used to parse the MAC-Address from the json string, 
    which is written to the device column of the kismet database.
    
    :param dev: json string from the kismet database column "device"
    
    :return: MAC-Address as string
    :rtype string
    """
    if 'kismet.device.base.macaddr' in dev:
        return dev['kismet.device.base.macaddr']
    return ""
    

def parse_encryption(dev):
    """
    This fuction is used to parse the encryption type from the json string, 
    which is written to the device column of the kismet database.
    
    :param dev: json string from the kismet database column "device"
    
    :return: Encryption type as string
    :rtype: string
    """
    if 'kismet.device.base.crypt' in dev:
        return dev['kismet.device.base.crypt']
    return ""
    

def parse_frequency(dev):
    """
    This function is used to extract the frequency from the json string, 
    which is written to the device column of the kismet database.
    
    :param dev: json string from the kismet database column "device"
    
    :retrurn: Frequency as string
    :rtype: string
    """
    if 'kismet.device.base.frequency' in dev:
        return dev['kismet.device.base.frequency']
    return ""
    
    
def parse_channel(dev):
    """
    This function is used to extract the channel from the json string, 
    which is written to the device column of the kismet database.
    
    :param dev: json string from the kismet database column "device"
    
    :retrurn: Channelnumber as string
    :rtype: string
    """
    if 'kismet.device.base.channel' in dev:
        return dev['kismet.device.base.channel']
    return ""
    

def parse_manufacturer(dev):
    """
    This function is used to extract the manufacturer name from the json 
    string, which is written to the device column of the kismet database.
    
    :param dev: json string from the kismet database column "device"
    
    :retrurn: Manufacturer name as string
    :rtype: string
    """
    if 'kismet.device.base.manuf' in dev:
        return dev['kismet.device.base.manuf']
    return ""
  
    



def does_ssid_matches(dev, ssid):
    """
    checks if the device SSID matches the given SSID string.
    
    :param dev: json string from the kismet database column "device"
    :param ssid: SSID string or regex 
    
    :return : true if the SSID matches, false otherwise
    :rtype: boolean
    """
    matched = False
    for s in dev['dot11.device']['dot11.device.advertised_ssid_map']:
        if re.match(ssid, dev['dot11.device']['dot11.device.advertised_ssid_map'][s]['dot11.advertisedssid.ssid']):
            matched = True
            break
    return matched
   
