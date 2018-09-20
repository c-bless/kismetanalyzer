This library can be used to analyze the results of the new Kismet version. 


The following scripts will be installed:

1. **kismet_analyzer_aplist:** This script can be used to extract access points from the SQLite database **.kismet* and export these results to *csv* and *kml*.


## Installation:
This library requires *simplekml* for exporting extracted information to *kml*. You can use *pip* to install the neccessary requirement.
```
pip install -r requirements.txt
```

The setup script can be used to install the library and requirements. It will create the above listed console commands.
```
python setup.py install
```

## Usage:


