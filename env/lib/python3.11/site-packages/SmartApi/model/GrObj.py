from SmartAPI.model.Obj import Obj
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from rdflib import XSD
from SmartAPI.common.Tools import Tools

class GrObj(Obj):
    '''
    classdocs
    '''

    def __init__(self, uri = None):        
        super(GrObj, self).__init__(uri)
        self.grName = None
        self.grDescription = None
    
    def hasGrName(self):  
        return self.grName is not None
    
    def setGrName(self, gname):
        self.grName = gname
        
    def getGrName(self):
        return self.grName  
    
    def hasGrDescription(self):
        return self.grDescription is not None
    
    def getGrDescription(self):
        return self.grDescription
    
    def setGrDescription(self, gdescription):
        self.grDescription = gdescription
        
    def serialize(self, model):
        '''
        return a rdf.Resource
        '''
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        if Tools.serializedObjs.has_key(self):
            return Tools.serializedObjs.get(self)        
        
        resource = super(GrObj, self).serialize(model)
        if self.hasGrName():
            resource.addProperty(model.createProperty( PROPERTY.NAME), model.createTypedLiteral(self.grName, XSD.string))  
        if self.hasGrDescription():
            resource.addProperty(model.createProperty( PROPERTY.GR_DESCRIPTION), model.createTypedLiteral(self.grDescription, XSD.string))      
        
        return resource
    
    def parseStatement(self, statement):
        
        # get predicate
        predicate = str(statement.getPredicate())
        
        if predicate==PROPERTY.NAME:
            self.setGrName(statement.getString())
            return
        
        if predicate == PROPERTY.GR_DESCRIPTION:
            self.setGrDescription(statement.getString())
            return
        
        super(GrObj, self).parseStatement(statement)
    