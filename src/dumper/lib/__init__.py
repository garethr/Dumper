import os
from xml.etree import ElementTree
from xml.etree.ElementTree import tostring


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
