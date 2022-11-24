#!/usr/bin/env python

# Author @vsoch, Written February 2020
# Updated June 2020, removing locations lookup testing (no longer used)
# Updated November 2022 for hpc.social
# Read in the locations.csv to validate each entry

import os
import csv
here = os.path.dirname(os.path.abspath(__file__))


def read_rows(filepath, newline="", delim=","):
    """read in the data rows of a csv file.
    """
    # Read in the entire membership counts
    with open(filepath, newline=newline) as infile:
        reader = csv.reader(infile, delimiter=delim)
        data = [row for row in reader]
    return data


def test_group_locations(tmp_path):
    filepath = os.path.join(os.path.dirname(here), "_data", "group-locations.csv")
    assert os.path.exists(filepath)
    lines = read_rows(filepath)

    # 1. Check that header is correct
    print("1. Checking that header has name, lat, lng, count")
    header = lines.pop(0)
    assert header[0] == "address"
    assert header[1] == "lat"
    assert header[2] == "lng"
    assert header[3] == "name"


def test_locations(tmp_path):
    """The locations.csv file is a comma separated file of locations.
       Each should have a name (lowercase), latitude, and longitude.
    """
    filepath = os.path.join(os.path.dirname(here), "_data", "locations.csv")
    assert os.path.exists(filepath)
    lines = read_rows(filepath)

    # 1. Check that header is correct
    print("1. Checking that header has name, lat, lng, count")
    header = lines.pop(0)
    assert header[0] == "address"
    assert header[1] == "lat"
    assert header[2] == "lng"
    assert header[3] == "count"
    assert header[4] == 'name'

    # 2. Check that name is all lowercase
    print("Checking names, latitudes, longitudes, and counts != 0")
    for line in lines:
        name = line[4]
        lat = line[1]
        lng = line[2]
        count = line[3]
        address = line[0]

        print("Testing %s" % address)
        assert address.lower() == address
        assert float(lat)
        assert float(lng)
        assert int(count)
        assert int(count) != 0
