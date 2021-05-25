from kismetanalyzer.util import parse_encryption, parse_channel, parse_loc, parse_frequency, parse_networkname, \
    parse_manufacturer, parse_mac, parse_clientmap, parse_name, parse_type, parse_phyname, parse_commonname

class Location(object):

    def __init__(self, lon= "0", lat ="0", alt ="0"):
        self._lon = lon
        self._lat = lat
        self._alt = alt

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, value="0"):
        self._lon = value

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, value="0"):
        self._lat = value

    @property
    def alt(self):
        return self._alt

    @alt.setter
    def alt(self, value="0"):
        self._alt = value

    def __str__(self):
        return "[Lon: {0}, lat: {1}, alt: {2}]".format(self._lon, self._lat, self._alt)


class AccessPoint(object):

    def __init__(self, ssid="", mac="", encryption="", location = None, frequency="", channel="",
                 manufacturer="", client_map=[]):
        self._ssid = ssid
        self._mac = mac
        self._encryption = encryption
        self._location = location
        self._frequency = frequency
        self._channel = channel
        self._manufacturer = manufacturer
        self._client_map = client_map

    @property
    def ssid(self):
        return self._ssid

    @ssid.setter
    def ssid(self, value=""):
        self._ssid = value

    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, value=""):
        self._mac = value

    @property
    def encryption(self):
        return self._encryption

    @encryption.setter
    def encryption(self, value=""):
        self._encryption = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value= None):
        if value is None:
            value = Location()
        self._location = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def client_map(self):
        return self._client_map

    @client_map.setter
    def client_map(self, value=[]):
        self._client_map = value


    @classmethod
    def from_json(cls, dev, strongest=False):
        ap = AccessPoint()
        lon, lat, alt = parse_loc(dev, strongest)
        loc = Location(lon, lat, alt)
        ap.location = loc
        ap.ssid = parse_networkname(dev)
        ap.mac = parse_mac(dev)
        ap.encryption = parse_encryption(dev)
        ap.frequency = parse_frequency(dev)
        ap.channel = parse_channel(dev)
        ap.manufacturer = parse_manufacturer(dev)
        ap._client_map = parse_clientmap(dev)
        return ap


class Device(object):

    def __init__(self, name="", commonname="", phyname="", location = None, frequency="", channel="",
                 manufacturer="", mac ="", type=""):
        self._name = name
        self._commonname = commonname
        self._phyname = phyname
        self._mac = mac
        self._type = type
        self._location = location
        self._frequency = frequency
        self._channel = channel
        self._manufacturer = manufacturer

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value=""):
        self._name = value

    @property
    def commonname(self):
        return self._commonname

    @commonname.setter
    def commonname(self, value=""):
        self._commonname = value

    @property
    def phyname(self):
        return self._phyname

    @phyname.setter
    def phyname(self, value=""):
        self._phyname = value


    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, value=""):
        self._mac = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value=""):
        self._type = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value= None):
        if value is None:
            value = Location()
        self._location = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value


    @classmethod
    def from_json(cls, dev, strongest=False):
        d = Device()
        lon, lat, alt = parse_loc(dev, strongest)
        loc = Location(lon, lat, alt)
        d.location = loc
        d.ssid = parse_networkname(dev)
        d.mac = parse_mac(dev)
        d.frequency = parse_frequency(dev)
        d.channel = parse_channel(dev)
        d.manufacturer = parse_manufacturer(dev)
        d.type = parse_type(dev)
        d.name = parse_name(dev)
        d.commonname = parse_commonname(dev)
        d.phyname = parse_phyname(dev)
        return d
