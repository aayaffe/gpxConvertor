import sys
import xml.etree.ElementTree
import gpxpy.gpx
from dateutil import parser

import files


def parse_file(path):
    return xml.etree.ElementTree.parse(path)


def identify_file(etree):
    r = etree.getroot().tag
    if r == "OCPNDraw":
        return 'draw'
    elif r == "gpx":
        return 'gpx'


input_valid = False
output_valid = False

if len(sys.argv) == 3:
    if files.is_file_exists_and_readable(sys.argv[1]):
        path_in = sys.argv[1]
        input_valid = True
    if files.is_path_exists_or_creatable_portable(sys.argv[2]):
        path_out = sys.argv[2]
        output_valid = True

while not input_valid:
    path_in = input("Please enter src file name (OCPN_Draw gpx):")
    if files.is_file_exists_and_readable(path_in):
        input_valid = True
    else:
        print("Input file is not valid!")
while not output_valid:
    path_out = input("Please enter dst file name (Standard gpx):")
    if files.is_path_exists_or_creatable_portable(path_out):
        output_valid = True
    else:
        print("Output file is not valid, or you do not have appropriate write permissions!")
f = parse_file(path_in)
target = open(path_out, 'w')
namespaces = {'opencpn': 'http://www.opencpn.org'}

if identify_file(f) == 'draw':
    gpx = gpxpy.gpx.GPX()
    for odpoint in f.getiterator("{http://www.opencpn.org}ODPoint"):
        # Check for duplicate WPT
        matches = [x for x in gpx.waypoints if (
            (x.name == odpoint.find('name').text) and (x.latitude == odpoint.attrib.get('lat')) and (
                x.longitude == odpoint.attrib.get('lon')))]
        if len(matches) > 0:
            continue

        w1 = gpxpy.gpx.GPXWaypoint()
        w1.name = odpoint.find('name').text
        w1.latitude = odpoint.attrib.get('lat')
        w1.longitude = odpoint.attrib.get('lon')
        w1.symbol = odpoint.find('sym').text
        w1.extensions = {odpoint.find('{http://www.opencpn.org}guid'), odpoint.find('{http://www.opencpn.org}viz'),
                         odpoint.find('{http://www.opencpn.org}viz_name'),
                         odpoint.find('{http://www.opencpn.org}arrival_radius'),
                         odpoint.find('{http://www.opencpn.org}ODPoint_range_rings'),
                         odpoint.find('{http://www.opencpn.org}type'),
                         odpoint.find('{http://www.opencpn.org}boundary_type')}
        w1.type = 'WPT'
        time = parser.parse(odpoint.find('time').text)
        w1.time = time
        gpx.waypoints.append(w1)
    print(gpx.to_xml(version="1.0")) #TODO: Should be 1.1 to include extensions
    target.write(gpx.to_xml(version="1.0"))
else:
    print("File is not ODraw format")