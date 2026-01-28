"""
A wrapper class around Python RDFLib methods to make a graph behave in a similar
way as Java Apache Jena model.
"""

from SmartAPI.rdf.Resource import Resource


class Statement(object):
    def __init__(self, id = None, model = None, subject = None, predicate = None, object = None, resource = None):
        self.id = id
        self.model = model
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.resource = resource
    
    def __repr__(self):
        return "<Statement at " + hex(id(self)) + ", s = " + str(self.subject) + ", p = " + str(self.predicate) + ", o = " + str(self.object) + ">"
        
    def toString(self):
        if self.object is not None:
            return unicode(self.object)
        return None
    
    def getString(self):
        return self.toString()
    
    def getBoolean(self):
        if self.object is not None:
            return str(self.object) == "true"
        return None
    
    def getDouble(self):
        if self.object is not None:
            return float(self.object)
        return 0.0
    
    def getFloat(self):
        if self.object is not None:
            return float(self.object)
        return 0.0
    
    def getInt(self):
        if self.object is not None:
            return int(self.object)
        return 0
    
    def getSubject(self):
        return self.subject
    
    def getPredicate(self):
        return self.predicate
    
    def getObject(self):
        return self.object

    def setSubject(self, s):
        self.subject = s
    
    def setPredicate(self, p):
        self.predicate = p
        
    def setObject(self, o):
        self.object = o

    def getModel(self):
        return self.model
    
    def setResource(self, r):
        self.resource = r
        
    def getResource(self):
        return self.resource
    