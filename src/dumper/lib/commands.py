import sys
import ConfigParser

from dumper import Dumper

def main(args):
    "Run the dumper command app"
    try:
        config = ConfigParser.RawConfigParser()
        config.read(args[1])
    except IndexError:
        print "You must pass a configuration file as the first agument"
        sys.exit(2)

    DumperClass = Dumper('mysql')
    dumper = DumperClass(config)
    dumper.dump()