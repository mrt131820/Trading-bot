from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.AbstractEntity import AbstractEntity
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj
from SmartAPI.common.Tools import Tools

import traceback


class Service(AbstractEntity):

	def __init__(self, uri = None):
		AbstractEntity.__init__(self, uri)
		self.managedBy = None
		self.setType(RESOURCE.SERVICE);

	def hasManagedBy(self):
		return self.managedBy is not None

	def setManagedBy(self, o):
		if isinstance(o, Obj):
			self.managedBy = o
		else:
			self.managedBy = Obj(o)
		
	def getManagedBy(self):
		return self.managedBy
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		service = super(Service, self).serialize(model)
		
		# set system uri
		if self.hasManagedBy():
			service.addProperty(model.createProperty( PROPERTY.ISMANAGEDBY ), self.managedBy.serialize(model))

		return service
	
	
	def parseStatement(self, statement):
		from SmartAPI.model.Obj import Obj
		from SmartAPI.model.InterfaceAddress import InterfaceAddress
				
		# get predicate
		predicate = str(statement.getPredicate())

		# managedby
		if predicate == PROPERTY.ISMANAGEDBY:
			try:
				self.managedBy = Obj().parse(statement.getResource())
			except:
				print "Unable to interpret seas:isManagedBy value as resource."
				traceback.print_exc() 

		# pass on to Object
		super(Service, self).parseStatement(statement)

