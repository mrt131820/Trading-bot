from SmartAPI.model.GrObj import GrObj
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from rdflib import XSD
from SmartAPI.rdf.Variant import Variant
from SmartAPI.common.Tools import Tools
import traceback


class PriceSpecification(GrObj):
    '''
    classdocs
    '''


    def __init__(self, uri = None):
        super(PriceSpecification, self).__init__(uri)
        #String 
        self.currency = None
        #Float 
        self.currencyValue = None
        #Data
        self.validFrom = None
        #Date 
        self.validThrough =  None
        # Boolean 
        self.valueAddedTaxIncluded = None
        # Variant 
        self.vatPercentage = None
        # String
        self.quantity = None
        # String
        self.unit = None
    
    def hasCurrency(self):
        return self.currency is not None
    
    def getCurrency(self):
        return self.currency
    
    def setCurrency(self, cur):
        self.currency = cur
    
    def hasQuantity(self):
        return self.quantity is not None
    
    def getQuantity(self):
        return self.quantity
    
    def setQuantity(self, q):
        '''
        @param q: URL string of this Quantity
        '''
        self.quantity = q
    
    def hasUnit(self):
        return self.unit is not None
    
    def getUnit(self):
        return self.unit
    
    def setUnit(self, u):
        '''
        @param u: URL string of this unit
        '''
        self.unit = u
    
    def hasCurrencyValue(self):
        return self.currencyValue is not None
    
    def getCurrencyValue(self):
        return self.currencyValue
    
    def setCurrencyValue(self, cv):
        self.currencyValue = cv
        
    def hasValidThrough(self):
        return self.validThrough is not None
    
    def getValidThrough(self):
        return self.validThrough
    
    def setValidThrough(self, vt):
        self.validThrough = vt
        
    def hasValidFrom(self):
        return self.validFrom is not None
    
    def getValidFrom(self):
        return self.validFrom
    
    def setValidFrom(self, vf):
        self.validFrom = vf
    
    def hasValueAddedTaxIncluded(self):
        return self.valueAddedTaxIncluded is not None
    
    def getValueAddedTaxIncluded(self):
        return self.valueAddedTaxIncluded
    
    def setValueAddedTaxIncluded(self, vat):
        self.valueAddedTaxIncluded = vat
    
    def hasVatPercentage(self):  
        return self.vatPercentage is not None
    
    def getVatPercentage(self): 
        return self.vatPercentage
    
    def setVatPercentage(self, vp):
        if isinstance(vp, Variant):
            self.vatPercentage = vp
        else: # if int, double,...
            self.vatPercentage = Variant(vp)
    
    def serialize(self, model):
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        if Tools.serializedObjs.has_key(self):
            return Tools.serializedObjs.get(self)        
        
        resource = super(PriceSpecification, self).serialize(model)
        
        #currency
        if self.hasCurrency():
            resource.addProperty(model.createProperty( PROPERTY.HASCURRENCY ), model.createTypedLiteral(self.currency, XSD.string))
        
        #currencyValue
        if self.hasCurrencyValue():
            resource.addProperty(model.createProperty( PROPERTY.HASCURRENCYVALUE ), model.createTypedLiteral(self.getCurrencyValue(), XSD.float))
        
        #validThrough
        if self.hasValidThrough():
            resource.addProperty(model.createProperty( PROPERTY.VALIDTHROUGH), model.createLiteral(self.getValidThrough()))
        
        #validFrom
        if self.hasValidFrom():
            resource.addProperty(model.createProperty( PROPERTY.VALIDFROM), model.createLiteral(self.getValidFrom()))
            
        # valueAddedTaxIncluded
        if self.hasValueAddedTaxIncluded():
            resource.addProperty(model.createProperty( PROPERTY.VALUEADDEDTAXINCLUDED),
                                 model.createTypedLiteral(self.getValueAddedTaxIncluded(), XSD.boolean ))    
        
        # vatPercentage
        if self.hasVatPercentage():
            resource.addProperty(model.createProperty(PROPERTY.VATPERCENTAGE), self.vatPercentage.serialize(model))
            
        # unit
        if self.hasUnit():
            resource.addProperty(model.createProperty(PROPERTY.UNIT), model.createResource(self.getUnit()))
            
        # quantity
        if self.hasQuantity():
            resource.addProperty(model.createProperty(PROPERTY.QUANTITYKIND), model.createResource(self.getQuantity()))
        
        return resource   
    
    def parseStatement(self, statement):
        
        # get predicate
        predicate = str(statement.getPredicate())
        
        if predicate == PROPERTY.HASCURRENCY:
            try:
                self.setCurrency(statement.getString())    
            except:
                print "Unable to interpret gr:hasCurrency value as literal string."
                traceback.print_exc()
            return  
        
        if predicate == PROPERTY.HASCURRENCYVALUE: 
            try:
                self.setCurrencyValue(statement.getFloat())
            except:
                print "Unable to interpret gr:hasCurrencyValue value as literal float."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VALIDTHROUGH:
            try:
                self.setValidThrough(statement.getObject().toPython())
            except:                
                print "Unable to interpret gr:validThrough value as date literal."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VALIDFROM:
            try:
                self.setValidFrom(statement.getObject().toPython())                
            except:                
                print "Unable to interpret gr:validFrom value as date literal."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VALUEADDEDTAXINCLUDED:
            try:
                self.setValueAddedTaxIncluded(statement.getBoolean())
            except:
                print "Unable to interpret gr:valueAddedTaxIncluded value as literal boolean."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.UNIT:
            try:
                self.setUnit(statement.getResource().toString())
            except:
                print "Unable to interpret seas:unit value as resource."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.QUANTITYKIND:
            try:
                self.setQuantity(statement.getResource().toString())
            except:
                print "Unable to interpret seas:quantityKind value as resource."
                traceback.print_exc()
            return
        
        if predicate == PROPERTY.VATPERCENTAGE:            
            self.setVatPercentage(Variant().parse(statement))
            return
        
        super(PriceSpecification, self).parseStatement(statement)  