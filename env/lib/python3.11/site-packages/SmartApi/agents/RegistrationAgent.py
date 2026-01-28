#!/usr/bin/python

""" 
An example class for making a registration to the SMARTAPI registry using Python
"""

import sys

from SmartAPI.agents.Agent import Agent
from SmartAPI.factory.RequestFactory import RequestFactory
from SmartAPI.common.SmartAPICrypto import SmartAPICrypto
from SmartAPI.common.Tools import Tools
from SmartAPI.common.HttpClient import HttpClient
from SmartAPI.common.SERIALIZATION import SERIALIZATION
from SmartAPI.common.CONTENTTYPES import CONTENTTYPE
from SmartAPI.smartapiexceptions.InsufficientDataException import InsufficientDataException

REGISTRATION_SERVER_ADDRESS = "http://seas.asema.com/webapps/rs/v1.0e1.0/register"
REGISTRATION_KEY_ADDRESS = "http://seas.asema.com/webapps/rs/v1.0e1.0/key"


class RegistrationAgent(Agent):
    def __init__(self, identity):
        Agent.__init__(self)
        self.identity = identity
        self.timestamp = None
        self.entities = []
        self.serialization = SERIALIZATION.TURTLE
  
        
    def registrate(self, entity = None, callback = None):
        messageBody, encryptionKey = self.generateEncryptedRegistrationMessage(entity = entity)
        
        encrypted_response = self.runQuery(REGISTRATION_SERVER_ADDRESS, CONTENTTYPE.TURTLE, CONTENTTYPE.TURTLE, messageBody)
        decrypted_response = SmartAPICrypto().symmetricDecrypt(encryptionKey, encrypted_response)
        
        return True
    
    def generateEncryptedRegistrationMessage(self, serverPublicKey = None, entity = None):
        if serverPublicKey is None:
            serverPublicKey = self.getServerPublicKey()
            
        messageBody = None
        symmetricKey = None
        msg = self.generateRegistrationMessage(entity)

        # Encrypt data
        if (msg is not None and serverPublicKey is not None):
            messageBody, symmetricKey = SmartAPICrypto().asymmetricEncrypt(serverPublicKey, msg)

        return messageBody, symmetricKey
    
    def generateRegistrationMessage(self, entity = None):
        if entity:
            self.addEntity(entity)
            
        # check that there is something to register
        if len(self.entities) < 1:
            raise InsufficientDataException("No SMARTAPI entities found in registration.")

        # build registration request
        request = RequestFactory().createRegistrationRequest(self.identity)

        for e in self.entities:
            request.addEntity(e)
            
        # store timestamp for later to check if registration was successful
        self.timestamp = request.getGeneratedAt();
        
        return Tools().toString(request, self.serialization)
    
    def setRegistrantUri(self, uri):
        self.generatedBy = uri

    def getRegistrantUri(self):
        return self.generatedBy

    def setRegistrationServiceUri(self, uri):
        self.rsUri = uri

    def getRegistrationServiceUri(self):
        return self.rsUri

    def addEntity(self, entity):
        self.entities.append(entity)
        

    def entitiesSize(self):
        return len(self.entities)
    
    def clearEntities(self):
        self.entities = []
        
    def getSerialization(self):
        return self.serialization

    def setSerialization(self, serialization):
        self.serialization = serialization
    
    def getServerPublicKey(self):
        keyString = ""
        key = None
        try:
            keyString = HttpClient().sendGet(REGISTRATION_KEY_ADDRESS)
            key = SmartAPICrypto().extractPemFormatPublicKey(keyString, "RSA");
        except:
            print "Failed to get a key from the registration server."
            print sys.exc_info()[1]
        return key
    