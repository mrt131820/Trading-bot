from SmartAPI.model.GrObj import GrObj
from SmartAPI.model.SystemOfInterest import SystemOfInterest
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from isodate.duration import Duration
from rdflib import XSD
import isodate
import traceback
from rdflib.term import Literal
from SmartAPI.common.Tools import Tools

class SomeItems(GrObj):
    '''
    classdocs
    '''


    def __init__(self, uri = None, type=None, name=None, description=None, systemOfInterestSameAs=None):
        super(SomeItems, self).__init__(uri)
        self.setType(RESOURCE.SOMEITEMS)
        if type is not None:
            self.addType(type)
        if name is not None:
            self.setName(name)
        if description is not None:
            self.setDescription(description)
        
        self.systemOfInterest = None
        if systemOfInterestSameAs is not None:
            self.setSystemOfInterestWithSameAs(systemOfInterestSameAs)      
            
        self.duration = None 
        
    def hasSystemOfInterest(self):
        return self.systemOfInterest is not None
    
    def getSystemOfInterest(self):
        return self.systemOfInterest
    
    def setSystemOfInterest(self, system):
        self.systemOfInterest = system
        
    def setSystemOfInterestWithSameAs(self, sameAs):
        soi = SystemOfInterest()
        soi.setSameAs(sameAs)
        self.setSystemOfInterest(soi)
        
    def setSystemOfInterestWithType(self, *types):
        soi = SystemOfInterest()
        soi.clearTypes()
        for t in types:
            soi.addType(t)
            
        self.setSystemOfInterest(soi)
        
    def hasDuration(self):
        return self.duration is not None
    def getDuration(self):
        '''
        @return: isodate module's Duration Object, which corresponds to XML duration type
        '''
        return self.duration
    
    def setDuration(self, *args):
        '''
        It can take either single parameter, or six parameters.
        @param  : if single parameter, then its type has to be either String or isodate.Duration type. If string, then
        the string has to align with ISO 8601 standard, with the format like "PnYnMnDTnHnMnS". 
        See: https://www.w3.org/TR/xmlschema-2/#duration
        
        If 6 parameters, then all of them need to be integers, representing years, months, days, hourse, minutes, seconds.           
        '''
        args = list(args)
        try:
            if len(args)==1:
                duration = args[0]
                if isinstance(duration, Duration):
                    self.duration = duration
                elif isinstance(duration, str) or isinstance(duration, unicode):                
                    self.duration = isodate.parse_duration(duration)
                else:
                    raise("wrong parameter type: "+type(duration))
            else:
                self.duration = Duration(args[0], args[1], args[2], args[3], args[4], args[5])
        except:
            traceback.print_exc()                           
                            
        
    def serialize(self, model):        
        '''
        return a rdf resource
        '''
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        if Tools.serializedObjs.has_key(self):
            return Tools.serializedObjs.get(self)                        
        
        resource = super(SomeItems, self).serialize(model)
        if self.hasSystemOfInterest():
            resource.addProperty(model.createProperty(PROPERTY.SYSTEMOFINTEREST), self.systemOfInterest.serialize(model) )
        # duration        
        if self.hasDuration():           
            resource.addProperty(model.createProperty( PROPERTY.DURATION ), model.createTypedLiteral(isodate.duration_isoformat(self.getDuration()), XSD.duration))
                
        return resource
        
    def parseStatement(self, statement):
        # get predicate
        predicate = str(statement.getPredicate())
        if predicate == PROPERTY.SYSTEMOFINTEREST:
            try:
                self.setSystemOfInterest(SystemOfInterest.parse(statement.getResource()))
            except:
                print "Unable to interpret seas:systemOfInterest value as resource."
                traceback.print_exc()
            return
        if predicate == PROPERTY.DURATION:
            try:
                self.setDuration(statement.getString())
            except:
                print "Unable to interpret seas:duration value as string literal."
                traceback.print_exc()           
            return
        super(SomeItems, self).parseStatement(statement)    
                  
        