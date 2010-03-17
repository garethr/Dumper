import os
import sys
import ConfigParser

import MySQLdb
import MySQLdb.cursors
import simplejson

from lib.filesystem import ensure_dir, create_or_update
from lib import dict_to_xml


def Dumper(type):
    "Factory function which returns a matching class"
    for cls in BaseDumper.__subclasses__():
        if cls.is_dumper_for(type):
            return cls
    raise ValueError

class BaseDumper(object):
    "Base class from which all dumpers should inherit"
    
    # control whether or not to print output
    verbosity = 1
    mode = 'individual'
    pre_processors = []
    post_processors = []
        
    def register_pre(self, processor):
        "Registers a processor into the processor queue"
        if processor not in self.pre_processors:
            self.pre_processors.append(processor)
            
    def register_post(self, processor):
        "Registers a processor into the processor queue"
        if processor not in self.post_processors:
            self.post_processors.append(processor)
    
    def inform(self, created, updated, file_name):
        "Simple wrapper for informing the caller about changes"
        if self.verbosity:
            if created:
                print "\033[1;33m[Created]\033[1;m %s" % file_name
            if updated:
                print "\033[1;34m[Updated]\033[1;m %s" % file_name
        
    def output_json(self, struct, record):
        "Default json output"
        file_name = "%s.json" % record
        # convert the data structure to json
        output = simplejson.dumps(struct)
        created, updated = create_or_update(output, file_name)
        # print output
        self.inform(created, updated, file_name)

    def output_xml(self, struct, record):
        "Default xml output"
        file_name = "%s.xml" % record
        # convert the data structure to xml
        
        if type(struct) == dict:
            output = dict_to_xml(struct, 'element')
        if type(struct) in (tuple, list):
            output = ""
            for item in struct:
                output = output + dict_to_xml(item, 'element')
            output = "<elements>%s</elements>" % output
        
        # we can alter the XML output using code if we want
        for processor in self.post_processors:
            output = processor(output)

        created, updated = create_or_update(output, file_name)
        # print output
        self.inform(created, updated, file_name)
        
    def dump(self, output_location):
        "Generate output"

        full_path = "%s/%s" % (output_location, self.path)

        if self.mode == 'individual':
            # see if the folder PATH exists and if not create it
            if ensure_dir(full_path):
                print "\033[1;33m[Created]\033[1;m %s" % full_path
            
            # placeholder for list for index page
            index = []
            
            results = self.results
            # we can alter the data structure using code if we want
            for processor in self.pre_processors:
                results = processor(results)

            for result in results:
                # filename based on the specified INDEX

                record = "%s/%s" % (full_path, result[self.index])
                self.output_json(result, record)
                self.output_xml(result, record)

                # we also want an index page so as we loop through we
                # create a list of all the individual items based
                # on the specified index value
                index.append({
                    self.index: result[self.index],
                    "url":  "/%s/%s" % (self.path, result[self.index])
                })
                
            # we may have deleted records and so need to delete files
            # that are still lying around.
            
            # get an up to date list of what is required
            required_names = []
            for result in self.results:
                required_names.append(str(result[self.index]))
            
            # compare with a list of files and delete all others
            existing_names = os.listdir(full_path)
            for item in existing_names:
                item_name = item.split('.')[0]
                if not item_name in required_names:
                    os.unlink(os.path.join(full_path, item))
                    print "\033[1;31m[Deleted]\033[1;m %s/%s" % (full_path, item)
                
            # create the index page
            self.output_json(index, full_path)
            self.output_xml(index, full_path)
        elif self.mode == 'combined':
            results = self.results
            # we can alter the data structure using code if we want
            for processor in self.pre_processors:
                results = processor(results)
            
            self.output_json(results, full_path)
            self.output_xml(results, full_path)


class MySQLDumper(BaseDumper):
    "MySQL backend example dumper"

    @classmethod
    def is_dumper_for(cls, type):
        "The string passed in to the factory to get this class"
        return type == 'mysql'
    
    def __init__(self, config):
        "Parse the config file and setup the database connection"
        try:
            # load requierd database settings
            HOST = config.get('Database', 'host')
            USERNAME = config.get('Database', 'username')
            PASSWORD = config.get('Database', 'password')
            DATABASE = config.get('Database', 'database')

            # and settings used by this dumper
            self.sql = config.get('Database', 'sql')
            self.path = config.get('Dumper', 'path')
            self.index = config.get('Dumper', 'index')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), e:
            print e
            sys.exit(2)
            
        # options with default values
        try:
            PORT = config.getint('Database', 'port')
        except ConfigParser.NoOptionError:
            PORT = 3306
            
        try:
            self.mode = config.getint('Dumper', 'mode')
        except ConfigParser.NoOptionError:
            self.mode = 'individual'
            
        # create the database connection
        database = MySQLdb.connect(
                    host=HOST,
                    port=PORT,
                    user=USERNAME,
                    passwd=PASSWORD,
                    db=DATABASE)
        # get a cursor to make queries with
        cursor = MySQLdb.cursors.DictCursor(database)
        
        cursor.execute(self.sql)
        self.results = cursor.fetchall()
