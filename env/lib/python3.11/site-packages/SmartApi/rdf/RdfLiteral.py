"""
A wrapper class around Python RDFLib methods to make a graph behave in a similar
way as Java Apache Jena model.
"""

from rdflib import URIRef

class RdfLiteral(object):
    def __init__(self, v = None, d = None):
        self.value = v;
        self.dataType = URIRef(d);
    
    def getValue(self):
        return str(value)
    
    def getDataType(self):
        return self.dataType
