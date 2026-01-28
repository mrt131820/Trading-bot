#!/usr/bin/python

""" 
doing similar thing as old RegistrySearchAgent
"""

import sys
import json
import urllib, urllib2
import datetime
from pytz import timezone
from urlparse import urlparse
from SmartAPI.model.Entity import Entity
from SmartAPI.model.Coordinates import Coordinates
from SmartAPI.model.Ring import Ring
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.rdf.Variant import Variant
from SmartAPI.common.HttpClient import HttpClient
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.Tools import Tools
from SmartAPI.common.NS import NS
from SmartAPI.model.Condition import Condition
from SmartAPI.model.Obj import Obj
from isodate.duration import Duration

import traceback
from rdflib.term import URIRef


class SearchAgent(object):
    # uri of the SEAS registration service
    rsUri = "http://seas.asema.com/webapps/rs/v1.0e1.2/search" 
    debug = False
    
    def __init__(self, myUri=''):        
        self.generatedBy = myUri
        self.entity = Entity()
        self.entity.clearTypes()
        self.httpClient = HttpClient()
        self.serialization = 'text/turtle'
    
    def search(self):
        from SmartAPI.model.Response import Response
        
        # serialize data
        messageBody = self._generateSearchMessage()
        if self.debug:
            print '\n Request to SEAS Search Service:'
            print messageBody, '\n'
        
        try:
            # send message
            responseStr = self.httpClient.sendPost(self.rsUri, messageBody, self.serialization, self.serialization, seasMethod=self.httpClient.SMARTAPI_METHOD_REQUEST)[0]
            response = Response.fromString(responseStr, self.serialization)
            if response is not None:
                if self.debug:
                    print '\n Response from SEAS Search Service:'
                    print Tools.toString(response, self.serialization)
                    Tools.printErrors(response)
                return response.getEntities()
            else:
                if self.debug:
                    print '\n Response from SEAS Search Service:'
                    print responseStr, '\n'
                return None
        except:
            print 'Exception while sending an HTTP request to ', self.rsUri
            traceback.print_exc()
        
        
    def _generateSearchMessage(self):
        from SmartAPI.factory.RequestFactory import RequestFactory
    
        request = RequestFactory().create(self.generatedBy)        
        request.setMethod(RESOURCE.READ)        
        request.addEntity(self.entity)
        
        return Tools.toString(request, self.serialization)       
    
    @classmethod
    def searchByNameAndType(cls, mySeasUri, freshnessInDays, keywords, types):
        '''
        @type keywords, types: list of Strings
        @type freshnessInDays: integer
        @type mySeasUri: String
        '''
        agent = SearchAgent(mySeasUri)
        agent.anyOfTypes(types)
        agent.daysOldData(freshnessInDays)
        agent.anyOfNames(keywords)
        return agent.search()
    
    @classmethod
    def searchByDescription(cls,  mySeasUri, freshnessInDays, searchString, types = [RESOURCE.ENTITY]):
        agent = SearchAgent(mySeasUri)        
        agent.anyOfTypes(types)
        agent.daysOldData(freshnessInDays)
        agent.ofDescription(searchString)
        return agent.search()
    
    @classmethod
    def searchById(cls, mySeasUri, freshnessInDays, searchString):
        agent = SearchAgent(mySeasUri)
        agent.ofType(RESOURCE.ENTITY);
        agent.ofId(searchString)
        agent.daysOldData(freshnessInDays)
        return agent.search()
    
    @classmethod
    def searchByPointAndType(cls, mySeasUri, freshnessInDays, latitude, longitude, distanceInKm, types):
        agent = SearchAgent(mySeasUri)
        agent.anyOfTypes(types)
        agent.daysOldData(freshnessInDays)
        
        coords = Coordinates(latitude=latitude, longitude=longitude)        
        agent.pointSearchArea(coords, distanceInKm)
        return agent.search()
    
    def pointSearchArea(self, center, kilometers):
        '''
        define circular search area
        '''
        ring = Ring()
        ring.add(URIRef(PROPERTY.LAT), center.getLatitude())
        ring.add(URIRef(PROPERTY.LONG), center.getLongitude())
        maxR = ValueObject()
        maxR.setQuantity(RESOURCE.LENGTH)
        maxR.setUnit(RESOURCE.KILOMETER)
        maxR.setValue(Variant(kilometers))
        ring.setMaxRadius(maxR)
        self.entity.add(URIRef(NS.SMARTAPI + "ring"), ring)
    
    def ofId(self, searchString):
        condition = Condition()
        condition.addRegex("(?i)" + searchString)
        self.entity.add(URIRef(PROPERTY.ID), condition)
    
    def ofDescription(self, searchString):
        condition = Condition()
        condition.addRegex("(?i)" + searchString)
        self.entity.add(URIRef(PROPERTY.COMMENT), condition)
       
    def ofType(self, type):
        '''
        define type to search
        '''
        if isinstance(type, str):
            type = URIRef(type)
        self.entity.addType(type)
        
    def anyOfTypes(self, types):
        '''
        Define all the types that can match
        '''
        if len(types) == 1:
            self.ofType(types[0])
        elif len(types) > 1:
            condition = Condition()
            for type in types:
                condition.addOr(Obj(type))
            self.entity.clearTypes()
            self.entity.addType(condition)
            
    def daysOldData(self, days):
        '''
        Define how many days old data will be searched.
        '''
        duration = Duration(days=days)
        self.entity.add(URIRef(PROPERTY.FRESHNESS), duration)
        
    def monthsOldData(self, months):
        '''
        Define how many months old data will be searched.
        '''
        duration = Duration(months=months)
        self.entity.add(URIRef(PROPERTY.FRESHNESS), duration)
        
    def anyOfNames(self, searchStrings):
        '''
        Define multiple search strings for the entity name (label). Will return also partial hits 
        for any of the strings.
        '''
        if len(searchStrings) > 0:
            condition = Condition()
            for stri in searchStrings:
                condition.addRegex("(?i)" + stri)
            
            self.entity.add(URIRef(PROPERTY.RDFS_LABEL), condition);            
        
    