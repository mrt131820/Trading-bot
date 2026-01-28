"""
Compatibility types that make the Python RDFlib behave in a similar fashion as
Java Jena.
"""

from rdflib import Namespace

xsdNS = Namespace("http://www.w3.org/2001/XMLSchema#")

class XSDDatatypeWrapper(object):
    def __init__(self):
        pass
    
    def __getattr__(self, attr):
        if attr[:3] == "XSD":
            return xsdNS[attr[3:]]
        else:
            return xsdNS[attr]

XSDDatatype = XSDDatatypeWrapper()