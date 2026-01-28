from SmartAPI.model.Obj import Obj
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Activity import Activity
from SmartAPI.model.Entity import Entity
from SmartAPI.model.Message import Message
from SmartAPI.common.Tools import Tools
import traceback

class Transaction(Obj):
    '''
    classdocs
    '''


    def __init__(self, uri=None):
        super(Transaction, self).__init__(uri)
        self.setType(RESOURCE.TRANSACTION)      
        #Entity signer 
        self.signer = None
        # Message message
        self.message = None                
        
    def hasSigner(self):
        return self.signer is not None    
    def getSigner(self):
        return self.signer    
    def setSigner(self, signer):
        if isinstance(signer, Entity):       
            self.signer = signer
        elif isinstance(signer, str):
            e = Entity()
            e.setSameAs(signer)
            self.setSigner(e)
           
        
    def hasMessage(self):
        return self.message is not None
    def getMessage(self):
        return self.message
    def setMessage(self, message):
        self.message = message
        
    def serialize(self, model):
        if self.serializeAsReference:
            return self.serializeToReference(model)
        
        if Tools.serializedObjs.has_key(self):
            return Tools.serializedObjs.get(self)        
        
        resource = super(Transaction, self).serialize(model)        
        # signer
        if self.hasSigner():
            resource.addProperty(model.createProperty(PROPERTY.SIGNER), self.signer.serialize(model))
        # message
        if self.hasMessage():
            resource.addProperty(model.createProperty(PROPERTY.MESSAGE), self.message.serialize(model))        
        
        return resource
    
    def parseStatement(self, statement):
        # get predicate
        predicate = str(statement.getPredicate())
        
        if predicate == PROPERTY.SIGNER:
            try:
                self.setSigner(Entity.parse(statement.getResource()))
            except:
                print "Unable to interpret seas:signer value as resource."
                traceback.print_exc()
            return
        if predicate == PROPERTY.MESSAGE:
            try:
                self.setMessage(Message.parse(statement.getResource()))
            except:
                print "Unable to interpret message value as resource."
                traceback.print_exc()
            return
        
        
        super(Transaction, self).parseStatement(statement)
     
    