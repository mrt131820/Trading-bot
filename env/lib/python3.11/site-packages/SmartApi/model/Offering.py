from SmartAPI.model.GrObj import GrObj
from SmartAPI.model.Obj import Obj
from SmartAPI.model.SomeItems import SomeItems
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
import traceback
from SmartAPI.model.UnitPriceSpecification import UnitPriceSpecification
from SmartAPI.common.Tools import Tools

class Offering(GrObj):
    '''
    classdocs
    '''

    def __init__(self, uri=None, name=None, description= None ):
        super(Offering, self).__init__(uri)
        # set Type is important for invoking Tools().getResourceByType() function at later point
        self.setType(RESOURCE.OFFERING)
        self.setName(name)
        self.setDescription(description)
        self.businessFunction = None
        self.priceSpecifications = []
        self.includes = []
     
    def hasBusinessFunction(self):
        return self.businessFunction is not None
    
    def getBusinessFunction(self):
        return self.businessFunction
    
    def setBusinessFunctionFromString(self, bf):
        '''
        @type bf: string
        '''
        obj = Obj(bf)
        obj.clearTypes()
        self.businessFunction = obj
        
    def setBusinessFunction(self, bfObj):
        self.businessFunction=bfObj
    
    def hasPriceSpecification(self):
        return len(self.priceSpecifications) > 0
    
    def getPriceSpecification(self):
        return self.priceSpecifications 
    
    def addPriceSpecification(self, ps):
        self.priceSpecifications.append(ps)
        
    def hasIncludes(self):
        return len(self.includes) > 0
    
    def getIncludes(self):
        return self.includes
    
    def addIncludes(self, someitems):
        '''
        @type sometimes: SomeItems 
        '''
        self.includes.append(someitems)
    def addIncludesFromStrings(self, type, name, description, systemOfInterestSameAs=None):
        '''
        @type type, name, description, systemOfInterestSameAs: String
        '''
        self.includes.append(SomeItems(type=type, name=name, description=description, systemOfInterestSameAs=systemOfInterestSameAs))
    
    def serialize(self, model):
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        if Tools.serializedObjs.has_key(self):
            return Tools.serializedObjs.get(self)
        
        resource = super(Offering, self).serialize(model)
        
        #businessFunction
        if self.hasBusinessFunction():
            resource.addProperty(model.createProperty(PROPERTY.HASBUSINESSFUNCTION), model.createResource(self.businessFunction.getIdentifierUri()))
        
        #priceSpecifications
        if self.hasPriceSpecification():
            for ps in self.priceSpecifications:
                resource.addProperty(model.createProperty(PROPERTY.HASPRICESPECIFICATION), ps.serialize(model))
        
        #includes
        if self.hasIncludes():
            for someitems in self.includes:
                resource.addProperty(model.createProperty(PROPERTY.INCLUDES), someitems.serialize(model))
        
        return resource
    
    def parseStatement(self, statement):
        # get predicate
        predicate = str(statement.getPredicate())
        
        if predicate == PROPERTY.HASBUSINESSFUNCTION:
            try:
                self.setBusinessFunction(Obj.parse(statement.getResource()))
            except:
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.HASPRICESPECIFICATION:
            try:
                self.addPriceSpecification(UnitPriceSpecification.parse(statement.getResource()))
            except:
                print "Unable to interpret gr:hasPriceSpecification value as resource."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.INCLUDES:
            try:
                self.addIncludes(SomeItems.parse(statement.getResource()))
            except:
                print "Unable to interpret gr:includes value as resource."
                traceback.print_exc()
            return
        
        super(Offering, self).parseStatement(statement)
    