from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.model.AbstractEntity import AbstractEntity
from SmartAPI.rdf.Resource import Resource
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools

import traceback

class ServiceProvider(AbstractEntity):

	def __init__(self, uri = None):
		AbstractEntity.__init__(self, uri)
		self.services = []
		self.setType(RESOURCE.SERVICEPROVIDER)

	def setService(self, service):
		self.services = [service]
	
	def addService(self, service):
		self.services.append(service)

	def getServices(self):
		return self.services

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		entity = super(ServiceProvider, self).serialize(model);
		
		# set services
		offersService = model.createProperty( PROPERTY.OFFERSSERVICE )
		for service in self.services:
			entity.addProperty( offersService, service.serialize(model) )
		
		return entity
	
	def parseStatement(self, statement):
		from SmartAPI.model.Service import Service
				
		# get predicate
		predicate = str(statement.getPredicate())

		# offersservice
		if predicate == PROPERTY.OFFERSSERVICE:
			try:
				self.addService(Service().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:offersService value as resource."
				traceback.print_exc() 
			
			return

		# pass on to Object
		super(ServiceProvider, self).parseStatement(statement)
