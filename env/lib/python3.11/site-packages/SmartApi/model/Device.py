from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.PhysicalEntity import PhysicalEntity
from SmartAPI.rdf.Resource import Resource
from SmartAPI.common.Tools import Tools

import traceback

class Device(PhysicalEntity):

	def __init__(self, uri = None):
		PhysicalEntity.__init__(self, uri)
		self.managingSystemUri = None
		self.setType(RESOURCE.DEVICE);
	
	def hasManagingSystemUri(self):
		return self.managingSystemUri is not None

	def setManagingSystemUri(self, uri):
		self.managingSystemUri = uri
	
	def getManagingSystemUri(self):
		return self.managingSystemUri

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		device = super(Device, self).serialize(model)

		# set system uri
		if self.hasManagingSystemUri():
			system = model.createResource( self.managingSystemUri )
			device.addProperty(model.createProperty( PROPERTY.ISMANAGEDBY ), system)

		return device

	def parseStatement(self, statement):
		
			predicate = str(statement.getPredicate())

			# ismanagedby
			if predicate == PROPERTY.ISMANAGEDBY:
				try:
					self.setManagingSystemUri(statement.getString())
				except:
					print "Unable to interpret seas:isManagedBy value as resource."
					traceback.print_exc()
				return 
			
			# pass on to Object
			super(Device, self).parseStatement(statement)

