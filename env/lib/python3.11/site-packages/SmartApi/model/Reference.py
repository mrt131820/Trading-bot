from SmartAPI.model.Obj import Obj
from SmartAPI.common.RESOURCE import RESOURCE

class Reference(Obj):
    '''
    classdocs
    '''


    def __init__(self, uri=None, hashCode=None, signature=None, sessionKey=None, encryptionKeyType=None, notary=None):
        super(Reference, self).__init__(uri)
        self.setType(RESOURCE.REFERENCE)        
        
        self.setHashCode(hashCode)
        self.setSignature(signature)
        self.setSessionKey(sessionKey)
        if encryptionKeyType != None:
            self.setEncryptionKeyType(encryptionKeyType)
        if notary != None:
            self.setNotary(notary)
