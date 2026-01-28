#!/usr/bin/python

""" 
will be replaced by SearchAgent
"""

import sys
import traceback

from rdflib import URIRef

from SmartAPI.agents.Agent import Agent
from SmartAPI.model.Activity import Activity
from SmartAPI.model.Coordinates import Coordinates
from SmartAPI.model.Condition import Condition
from SmartAPI.model.Entity import Entity
from SmartAPI.model.Input import Input
from SmartAPI.model.Obj import Obj
from SmartAPI.model.Output import Output
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.rdf.Variant import Variant
from SmartAPI.model.Ring import Ring
from SmartAPI.model.Response import Response
from SmartAPI.factory.RequestFactory import RequestFactory
from SmartAPI.common.Tools import Tools
from SmartAPI.common.SERIALIZATION import SERIALIZATION
from SmartAPI.common.NS import NS
from SmartAPI.common.CONTENTTYPES import CONTENTTYPE
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY


content_type = "text/turtle"
REGISTRY_SEARCH_SERVER_ADDRESS = "http://seas.asema.com/webapps/rs/v1.0e1.1/search"

debug = False


class RegistrySearchAgent(Agent):
    def __init__(self, identity = None):
        Agent.__init__(self)
        self.identity = identity
        self.entity = Entity()
        self.entity.clearTypes()
        self.server_uri = REGISTRY_SEARCH_SERVER_ADDRESS
        self.serialization = SERIALIZATION.TURTLE
        
    def setSenderUri(self, generatedBy):
        self.identity = generatedBy
        
    def search(self):
        payload = self.generateSearchMessage()
        try :
            if debug:
                print "Request to SMARTAPI Search Service:"
                print payload

            resp_str = self.runQuery(self.server_uri, content_type, content_type, payload)
            
            response = Response().fromString(resp_str, self.serialization)
            if response != None:
                if debug:
                    print "Response from SMARTAPI Search Service:"
                    print resp_str
                return response.getEntities()
            else:
                if debug:
                    print "Response from SMARTAPI Search Service:"
                    print resp_str
                return None
        except:
            print "Exception while sending an HTTP request to " + REGISTRY_SEARCH_SERVER_ADDRESS
            traceback.print_exc()
            return None
        
    def clear(self):
        self.entity = Entity()
        
    def setEntity(self, searchEntity):
        self.entity = searchEntity

    def generateSearchMessage(self):
        request = RequestFactory().create(self.identity)
        request.setMethod(RESOURCE.READ)
        request.addEntity(self.entity)
        return Tools().toString(request, self.serialization)
        
    def setServiceUri(self, serviceUri):
        self.server_uri = serviceUri
        
    def ofDescription(self, searchString):
        condition = Condition()
        condition.addRegex("(?i)" + searchString)
        self.entity.add(URIRef(PROPERTY.COMMENT), condition)
        
    def anyOfNames(self, searchStrings):
        if len(searchStrings) > 0:
            condition = Condition()
            for s in searchStrings:
                condition.addRegex("(?i)" + s)
            self.entity.add(URIRef(PROPERTY.RDFS_LABEL), condition)
            
    def ofName(self, searchString, exactMatch=False):
        if exactMatch:
            self.entity.setName(searchString)
        else:
            condition = Condition()
            condition.addRegex("(?i)" + searchString)
            self.entity.add(URIRef(PROPERTY.RDFS_LABEL), condition)
            
    def ofPartialId(self, searchString):
        condition = Condition()
        condition.addRegex("(?i)" + searchString)
        self.entity.add(URIRef(PROPERTY.ID), condition)
            
    def ofType(self, type):
        self.entity.addType(type)
    
    def anyOfTypes(self, types):
        if len(types) == 1:
            self.ofType(types[0])
        if len(types) > 1:
            condition = Condition()
            for type in types:
                condition.addOr(Obj(type))
            self.entity.setType(condition)
            
    def clearTypes(self):
        self.entity.clearTypes()
        
    def ofInputType(self, type):
        if self.entity.hasCapability():
            a = self.entity.getCapabilities()[0]
            i = Input()
            i.setType(type)
            a.addInput(i)
        else:
            a = Activity()
            i = Input()
            i.setType(type)
            a.addInput(i)
            self.entity.addCapability(a)
        
    def ofOutputType(self, type):
        if self.entity.hasCapability():
            a = self.entity.getCapabilities()[0]
            o = Output()
            o.setType(type)
            a.addOutput(o)
        else:
            a = Activity()
            o = Output()
            o.setType(type)
            a.addOutput(o)
            self.entity.addCapability(a)
                
    def polygonSearchArea(self, polygon):
        self.entity.add(URIRef(RESOURCE.POLYGON), polygon)
        
    def multipolygonSearchArea(self, polygons):
        for polygon in polygons:
            self.entity.add(URIRef(RESOURCE.POLYGON), polygon)
        
    def rectangeSearchArea(self, minCoords, maxCoords):
        self.entity.add(URIRef(PROPERTY.MINLOCATION), minCoords)
        self.entity.add(URIRef(PROPERTY.MAXLOCATION), maxCoords)
        
    def pointSearchArea(self, center, kilometers):
        ring = Ring()
        ring.add(URIRef(PROPERTY.LAT), center.getLatitude())
        ring.add(URIRef(PROPERTY.LONG), center.getLongitude())
        maxR = ValueObject()
        maxR.setQuantity(RESOURCE.LENGTH)
        maxR.setUnit(RESOURCE.KILOMETER)
        maxR.setValue(Variant(kilometers))
        ring.setMaxRadius(maxR)
        self.entity.add(URIRef(NS.SMARTAPI + "ring"), ring)
        
    def debugMode(self, value):
        global debug
        debug = value
        
    def searchByPointAndType(self, myUri, latitude, longitude, distanceInKm, types):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        agent.anyOfTypes(types)
        coords = Coordinates()
        coords.setLatitude(latitude)
        coords.setLongitude(longitude)
        agent.pointSearchArea(coords, distanceInKm)
        return agent.search()
        
    def searchByNameAndType(self, myUri, keywords, types):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        agent.anyOfTypes(types)
        agent.anyOfNames(keywords)
        return agent.search()

    def searchServicesByOutputType(self, myUri, type):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        agent.ofType(RESOURCE.SERVICE)
        agent.ofOutputType(type)
        return agent.search()

    def searchServicesByInputType(self, myUri, type):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        agent.ofType(RESOURCE.SERVICE)
        agent.ofInputType(type)
        return agent.search()

    def searchByDescription(self, myUri, searchString, types = [RESOURCE.ENTITY]):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        agent.anyOfTypes(types)
        agent.ofDescription(searchString)
        return agent.search()

    def searchByPartialId(self, myUri, searchString):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        agent.ofPartialId(searchString)
        return agent.search()
        
    def fetchById(self, myUri, idToFetch):
        agent = RegistrySearchAgent()
        agent.clear()
        agent.setSenderUri(myUri)
        entity = Entity(idToFetch)
        entity.clearTypes()
        agent.setEntity(entity)
        resEntities = agent.search()
        if len(resEntities) > 0:
            return resEntities[0]
        else:
            return None
