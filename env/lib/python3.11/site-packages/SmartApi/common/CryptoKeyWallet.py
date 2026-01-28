from Crypto.PublicKey import RSA

class CryptoKeyWallet(object):
    privateKey = None    
    publicKey = None
    
    @classmethod
    def setPublicKey(cls, pkey):
        cls.publicKey = pkey 
       
    @classmethod   
    def setPrivateKey(cls, privkey):
        cls.privateKey = privkey
        
    @classmethod
    def getPrivateKey(cls):
        return cls.privateKey
    
    @classmethod
    def loadPrivateKey(cls, privkeyPath):    
        f = open(privkeyPath,'r')
        cls.privateKey = RSA.importKey(f.read())
        return cls.privateKey
    
    @classmethod
    def loadPublicKey(cls, pubkeyPath):
        f = open(pubkeyPath,'r')
        cls.publicKey = RSA.importKey(f.read())
        return cls.publicKey
    
        