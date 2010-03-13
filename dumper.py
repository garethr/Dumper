#!/usr/bin/env python

import os
import sys
import ConfigParser

import MySQLdb
import MySQLdb.cursors
import simplejson

config = ConfigParser.RawConfigParser()
try:
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
except ConfigParser.NoSectionError, e:
    print e
    sys.exit(2)

def create_or_update(content, filename):
    """
    Given some content and a filename either:
    - create the file and write the content to it if it doesn't exist
    - update the file contents if they differ
    - do nothing if the file hasn't changed
    """
    # work out whether we are creating, updating or doing nothing
    try:
        handle = open(filename, 'r')
        created = False 
        if not content == handle.read():
            updated = True
        else:
            updated = False
    except IOError:
        created = True
        updated = False
    
    # write the output to the file and close if we have to
    if created or updated:
        handle = open(filename, 'w')
        handle.write(content)
        handle.close()

    return created, updated

def ensure_dir(path):
    "Create directory if it doesn't already exist"
    directory = os.path.dirname("%s/" % path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False

if __name__ == '__main__':

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
        print "[Created] %s" % PATH
    
    # placeholder for list for index page
    index = []
    for result in results:
        # filename based on the specified INDEX
        file_name = "%s/%s.json" % (PATH, result[INDEX])
        # convert the data structure to json
        output = simplejson.dumps(result)
        created, updated = create_or_update(output, file_name)
        # print output
        if created:
            print "[Created] %s" % file_name
        if updated:
            print "[Updated] %s" % file_name
        # we also want an index page so as we loop through we
        # create a list of all the individual items based
        # on the specified index value
        index.append({
            INDEX: result[INDEX],
            "url":  "/%s/%s" % (PATH, result[INDEX])
        })
    # create the index page
    index_file_name = "%s.json" % PATH
    index_json = simplejson.dumps(index)
    created, updated = create_or_update(index_json, index_file_name)
    if created:
        print "[Created] %s" % index_file_name
    if updated:
        print "[Updated] %s" % index_file_name

