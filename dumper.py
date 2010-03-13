#!/usr/bin/env python

import sys
import ConfigParser

import MySQLdb
import MySQLdb.cursors

from lib import ensure_dir, output_json, output_xml


if __name__ == '__main__':
    
    try:
        config = ConfigParser.RawConfigParser()
        config.read(sys.argv[1])
    except IndexError:
        print "You must pass a configuration file as the first agument"
        sys.exit(2)

    try:
        HOST = config.get('Database', 'host')
        USERNAME = config.get('Database', 'username')
        PASSWORD = config.get('Database', 'password')
        DATABASE = config.get('Database', 'database')
        PORT = config.getint('Database', 'port')

        SQL = config.get('Options', 'sql')
        PATH = config.get('Options', 'path')
        INDEX = config.get('Options', 'index')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), e:
        print e
        sys.exit(2)
        
    database = MySQLdb.connect(
                host=HOST,
                port=PORT,
                user=USERNAME,
                passwd=PASSWORD,
                db=DATABASE)

    cursor = MySQLdb.cursors.DictCursor(database)
    cursor.execute(SQL)
    
    results = cursor.fetchall()

    # see if the folder PATH exists and if not create it
    if ensure_dir(PATH):
        print "\033[1;33m[Created]\033[1;m %s" % PATH
    
    # placeholder for list for index page
    index = []
    for result in results:
        # filename based on the specified INDEX
        
        record = "%s/%s" % (PATH, result[INDEX])
        output_json(result, record)
        output_xml(result, record)
        
        # we also want an index page so as we loop through we
        # create a list of all the individual items based
        # on the specified index value
        index.append({
            INDEX: result[INDEX],
            "url":  "/%s/%s" % (PATH, result[INDEX])
        })
    # create the index page
    output_json(index, PATH)
    output_xml(index, PATH)
