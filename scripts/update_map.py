#!/usr/bin/env python3

# Update map will retrieve locations via a csv, and then generate a new yaml file using lookup of schools
# https://docs.google.com/spreadsheets/d/e/2PACX-1vSTOdevfR0mk6QS9FFlKbVxlddg-M8mhhYIebh4sPtCktQvvkdRPY_rjUMR6May82aFWCjQaf915JHF/pub?output=tsv
# requests is required
# Yes, this is a bit spaghetti code. Even I like writing that way every so often!
# Copyright @vsoch, 2022

from geopy.geocoders import Nominatim


import requests
import sys

import os
import csv
import re
import time

here = os.path.dirname(os.path.abspath(__file__))


def get_filepath():
    """
    get path for the data file to write
    """
    return os.path.join(os.path.dirname(here), "_data", "locations.csv")


def get_group_filepath():
    """
    get path for the data file to write
    """
    return os.path.join(os.path.dirname(here), "_data", "group-locations.csv")


def get_locations_file():
    """
    get path for the locations already found
    """
    filepath = os.path.join(os.path.dirname(here), "_data", "locations.csv")
    if not os.path.exists(filepath):
        sys.exit("Cannot find %s" % filepath)
    return filepath


def get_location(geolocator, address, delay=1.5, attempts=3):
    """
    Retry to use the geolocator, fail after some number of attempts
    """
    try:
        time.sleep(delay)
        location = geolocator.geocode(address, timeout=10)
        return location
    except:
        if attempts > 0:
            return get_location(
                geolocator, address, delay=delay + 1, attempts=attempts - 1
            )
        raise


def write_rows(filepath, rows, sep=","):
    with open(filepath, "w", newline="") as outfile:
        writer = csv.writer(outfile, delimiter=sep)
        [writer.writerow(row) for row in rows]
    print("Wrote locations and counts to %s." % filepath)

def read_rows(filepath, newline="", delim=","):
    """
    read in the data rows of a csv file.
    """
    # Read in the entire membership counts
    with open(filepath, newline=newline) as infile:
        reader = csv.reader(infile, delimiter=delim)
        data = [row for row in reader]
    return data


def parse_location_line(line):
    """
    Given a location line, parse into a map metadata entry
    """
    # timestamp, state, city, country, individual (blank) or group, name
    parts = line.split("\t")
    state = parts[1].strip()
    city = parts[2].strip()
    country = parts[3].strip()

    is_individual = True
    name = None
    if len(parts) > 4:
        is_individual = parts[4].strip() in ["", None]
    if len(parts) > 5:
        name = parts[5].strip().replace(",", "-")
    entry = {
        "state": state,
        "city": city,
        "country": country,
        "is_individual": is_individual,
        "name": name,
    }

    address = "" if not city else city
    if state:
        address += f", {state}" if address else state
    if country:
        address += f", {country}" if address else country
    address = address.lower()

    for strip in [" ", ",", " ", ","]:
        address = address.strip(strip)
    entry["address"] = address
    return entry


def get_locations(lines):
    """
    Get locations and geolocate for location file.

    Returns locations, entries, missing
    """
    # These locations we've already found
    locations = read_rows(get_locations_file(), delim=",")

    assert locations[0] == ["address", "lat", "lng", "count", "name"]
    locations.pop(0)
    locations = {x[0]: x[1:] for x in locations}

    # Create geolocator
    geolocator = Nominatim(user_agent="hpc.social")

    # Get lats/long for each location, keep track of missing
    # This first step just cares about getting latitude and longitude
    missing = set()
    entries = []
    for line in lines:
        entry = parse_location_line(line)
        entries.append(entry)
        address = entry["address"]

        # This is explicitly to get locations matched to the names
        if address not in locations:

            print(f"Looking up {address}")
            location = get_location(geolocator, address)

            # Rate limit is 1 per second
            if location:
                lat = location.latitude
                lng = location.longitude
                locations[address] = [lat, lng]
            else:
                print(f"{address} is not found with geocoding." % address)
                missing.add(address)
    return locations, entries, missing


def get_google_sheet():
    """
    Read tab separated values sheet with locations!
    """
    # A tsv download for just the worksheet with city, state
    sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSTOdevfR0mk6QS9FFlKbVxlddg-M8mhhYIebh4sPtCktQvvkdRPY_rjUMR6May82aFWCjQaf915JHF/pub?output=tsv"

    # Ensure the response is okay
    response = requests.get(sheet)
    if response.status_code != 200:
        print(
            "Error with getting sheet, response code %s: %s"
            % (response.status_code, response.reason)
        )
        sys.exit(1)

    # Split lines by all sorts of fugly carriage returns
    lines = response.text.split("\r\n")

    # Remove empty responses, header row, make all lowercase
    lines = [x.strip('"').strip() for x in lines[1:] if x.strip()]
    return lines


def main():
    """
    main entrypoint for the script to generate the locations file
    """
    lines = get_google_sheet()
    locations, entries, missing = get_locations(lines)

    # Keep track of locations not known, counts known (individuals and groups)
    unknown = set()
    counts = {}

    # Now we just care about address and names
    names = {}

    # Now go through lines, but include each unique
    for entry in entries:
        if entry["address"] not in locations and entry["address"] != "remote":
            unknown.add(entry["address"])
            continue
        if entry["address"] not in names:
            names[entry["address"]] = {"count": 0, "names": set()}
        names[entry["address"]]["count"] += 1
        if entry["name"]:
            names[entry["address"]]["names"].add(entry["name"])

    # Alert user about unknown locations
    if unknown:
        print("UNKNOWN:\n %s\n" % "\n".join(unknown))
    if missing:
        print("MISSING:\n %s" % "\n".join(missing))

    # Generate list of individual names with latitude and longitude for each
    # Groups and individuals are kept separately
    # ["address", "lat", "lng", "count", "name"]
    updated = [["address", "lat", "lng", "count", "name"]]
    for address, entry in names.items():

        people = ""
        if entry["names"]:
            people = "|".join(list(entry["names"]))

        # We found a location (lat long) for the place!
        if address in locations and entry["count"] > 0:
            updated.append(
                [
                    address,
                    locations[address][0],
                    locations[address][1],
                    entry["count"],
                    people,
                ]
            )

    print("Found a total of %s locations, each with a count!" % (len(updated) - 1))

    # Write the new file
    write_rows(get_filepath(), updated)

    # Now update group locations
    groups = [["address", "lat", "lng", "name"]]

    for entry in entries:
        if entry["address"] not in locations and entry["address"] != "remote":
            continue
        if entry["name"]:
            groups.append(
                [entry['address'], locations[entry['address']][0], locations[entry['address']][1], entry["name"]]
            )
    write_rows(get_group_filepath(), groups)


if __name__ == "__main__":
    main()
