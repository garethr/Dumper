import os
from xml.etree import ElementTree
from xml.etree.ElementTree import tostring

import simplejson


def _ConvertDictToXmlRecurse(parent, dictitem):
    assert type(dictitem) is not type([])

    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.iteritems():
            if str(tag) == '_text':
                parent.text = str(child)
            elif type(child) is type([]):
                # iterate through the array and convert
                for listchild in child:
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _ConvertDictToXmlRecurse(elem, listchild)
            else:
                elem = ElementTree.Element(tag)
                parent.append(elem)
                _ConvertDictToXmlRecurse(elem, child)
    else:
        parent.text = str(dictitem)
    
def dict_to_xml(xmldict, element):
    """
    Converts a dictionary to an XML ElementTree Element 
    """

    root = ElementTree.Element(element)
    _ConvertDictToXmlRecurse(root, xmldict)
    return tostring(root)

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

def output_json(result, record):
    file_name = "%s.json" % record
    # convert the data structure to json
    output = simplejson.dumps(result)
    created, updated = create_or_update(output, file_name)
    # print output
    if created:
        print "\033[1;33m[Created]\033[1;m %s" % file_name
    if updated:
        print "\033[1;35m[Updated]\033[1;m %s" % file_name

def output_xml(struct, record):
    from lib import dict_to_xml
    file_name = "%s.xml" % record
    # convert the data structure to json

    if type(struct) == dict:
        output = dict_to_xml(struct, 'element')
    if type(struct) == list:
        output = ""
        for item in struct:
            output = output + dict_to_xml(item, 'element')
        output = "<elements>%s</elements>" % output

    created, updated = create_or_update(output, file_name)
    # print output
    if created:
        print "\033[1;33m[Created]\033[1;m %s" % file_name
    if updated:
        print "\033[1;35m[Updated]\033[1;m %s" % file_name
