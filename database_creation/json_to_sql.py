"""
JSON to SQL script

    This script takes JSON file with specific format and create a SQL database from it.

    :param filename: use filename as json file, 'database.json' by default
    :param help: display help
"""

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

import getopt
import sqlite3


def main(argv):
    json_filename = 'database.json'
    try:
        opts, args = getopt.getopt(argv, "hf:", ["help", "file="])
    except getopt.GetoptError:
        print("Arguments error. Please look at the help of the script.\n")
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            json_filename = arg

    if not os.path.isfile(json_filename):
        print("File error : ", json_filename, " does not exist.")
        sys.exit(2)

    db = sqlite3.connect('./database.db')

    c = db.cursor()
    # Query to check if the schema exists
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Idol' ''')

    if c.fetchone()[0] != 1:
        create_database_schema(db)

    populate_database(db, json_filename)


def usage():
    print("JSON to SQL script."
          "\nParameters :"
          "\n\t(--file | -f) name_of_the_json_file -> could be added to specify the json file."
          "\n\t--help | -h -> display this message.")


def create_database_schema(db):
    print("Creating database schema...")
    query = open('create_database.sql', 'r').read()

    c = db.cursor()
    c.executescript(query)
    db.commit()
    c.close()


def populate_database(db, json_filename):
    print("WIP")


if __name__ == "__main__":
    main(sys.argv[1:])
