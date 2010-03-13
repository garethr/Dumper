from fabric.api import *
from fabric.contrib.files import exists

def test():
    "Run sample configuration file"
    local('cd tests; python ../dumper.py people.truck')


def clean_tests():
    "Remove files created during test run"
    local('rm -rf tests/people')
    local('rm -rf tests/people.xml')
    local('rm -rf tests/people.json')
