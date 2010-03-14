import os
import sys
import shutil
import getopt
import ConfigParser

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

    for root, dirs, files in os.walk(directory):
        for f in files:
            os.unlink(os.path.join(root, f))
            print "\033[1;31m[Deleted]\033[1;m %s" % f
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
            print "\033[1;31m[Deleted]\033[1;m %s" % d
