import os
import sys
import ConfigParser
import getopt

from dumper import Dumper


def main(argv):
    "Run the dumper command app"
    
    # parse out arguments
    try:
        opts, args = getopt.getopt(argv, "ho:cu",
           ["help", "output=", "clean"])
    except getopt.GetoptError:
        # any errors exit
        usage()
        sys.exit(2)
    
    # default output to a directory called output
    output = 'output'
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # asked for help information
            usage()
            sys.exit()
        elif opt in ("-o", "--output"): 
            # set a different output dir
            output = arg
        elif opt in ("-c", "--clean"):
            # delete everything from the output dir and exit
            clean(output)
            sys.exit()
    
    # check we have a configuration file passed in, and that the 
    # file exists
    try:
        if not os.path.isfile(argv[-1]):
            print "You must specify an existing configuration file"
            sys.exit(2)
        
    except IndexError:
        print "You must pass a configuration file as the first agument"
        sys.exit(2)

    # parse the configuration file
    config = ConfigParser.RawConfigParser()
    config.read(argv[-1])

    # get the specified backend from the configuration file
    try:
        backend = config.get('Dumper', 'backend')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), e:
        # if we don't find anything then exit with an error
        print e
        sys.exit(2)

    # work out which class to use via the factory
    try:
        DumperClass = Dumper(backend)
    except ValueError:
        print "Specified backend %s doesn't exist" % backend
        sys.exit(2)
    # instantiate the relevant backend class
    dumper = DumperClass(config)
    # and finally create all the files
    dumper.dump(output)
    
def usage():
    "Print help information"
    print """Dumper. Static generator for web services. Usage: 
    
dumper [options] configuration_file

-o, --output [location]    defaults to output
-c, --clean                removes all files from the output directory
-h, --help                 display this help message
"""

def clean(directory):
    "Remove everything from the output directory"
    file_list = os.listdir(directory)
    for individual_file in file_list: 
        file_path = "%s/%s" % (directory, individual_file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
            print "\033[1;31m[Deleted]\033[1;m %s" % file_path
        if os.path.isdir(file_path):
            print "doesn't delete directories yet %s" % file_path
