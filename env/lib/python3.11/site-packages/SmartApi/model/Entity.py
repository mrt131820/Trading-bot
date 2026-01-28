from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj

from SmartAPI.common.Tools import Tools

import sys
import traceback
from rdflib.term import URIRef

class Entity(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.address = None
		self.coordinates = None
		self.zone = None
		self.managedBy = None
		self.creators = []
		self.owners = []
		self.controllabilities = []
		self.availabilities = []
		self.dataAvailabilities = []
		self.capabilities = []
		self.capacities = []
		self.managedEntities = []
		self.interfaces = []
		self.relatedUrls = {}
		self.valueObjects = []
		self.setType(RESOURCE.ENTITY)

	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
							
		entity = super(Entity, self).serialize(model)
		
		# zone
		if self.hasZone():
			entity.addProperty(model.createProperty( PROPERTY.ZONE ), self.zone.serialize(model))
		
		# address
		if self.hasAddress():
			entity.addProperty(model.createProperty( PROPERTY.HASADDRESS ), self.address.serialize(model))
		
		# managed by
		if self.hasManagedBy():
			entity.addProperty(model.createProperty( PROPERTY.ISMANAGEDBY ), self.managedBy.serialize(model))
			
		# coordinate
		if self.hasCoordinates():
			entity.addProperty(model.createProperty( PROPERTY.LOCATION ), self.coordinates.serialize(model))
		
		# controllability
		for controllability in self.controllabilities:
			entity.addProperty( model.createProperty( PROPERTY.HASEVALUATION ), controllability.serialize(model) )

		# availability
		for availability in self.availabilities:
			entity.addProperty( model.createProperty( PROPERTY.HASAVAILABILITY ), availability.serialize(model) )

		# data availability
		for availability in self.dataAvailabilities:
			entity.addProperty( model.createProperty( PROPERTY.HASDATAAVAILABILITY ), availability.serialize(model) )

		# capacities
		for cap in self.capacities:
			entity.addProperty(model.createProperty( PROPERTY.CAPACITY ), cap.serialize(model))
		
		# set interfaces
		for iAddrs in self.interfaces:
			entity.addProperty(model.createProperty( PROPERTY.INTERFACE ), iAddrs.serialize(model))
		
		# set owners
		for owner in self.owners:
			entity.addProperty(model.createProperty( PROPERTY.OWNER ), owner.serialize(model))
			
		# set creators
		for creator in self.creators:
			entity.addProperty(model.createProperty( PROPERTY.CREATOR ), creator.serialize(model))
			
		# capabilites
		hasCapabilityProp = model.createProperty( PROPERTY.HASCAPABILITY )
		for activity in self.capabilities:
			entity.addProperty( hasCapabilityProp, activity.serialize(model) )
		
		# managed entities
		managesProp = model.createProperty( PROPERTY.MANAGES )
		for e in self.managedEntities:
			entity.addProperty( managesProp, e.serialize(model) )
			
		# valueobjects		
		valueobjProp = model.createProperty( PROPERTY.VALUEOBJECT )
		for valueObject in self.valueObjects:
			entity.addProperty( valueobjProp, valueObject.serialize(model) )
		
		# websites
		if self.hasWebsite():
			websiteProp = model.createProperty( PROPERTY.HASURL )
			for website in self.relatedUrls["siteurls"]:
				entity.addProperty( websiteProp, website );
			
		# logos
		if self.hasLogo():
			logoProp = model.createProperty( PROPERTY.HASLOGO )
			for logo in self.relatedUrls["logos"]:
				entity.addProperty( logoProp, logo );
			
		# photos
		if self.hasPhoto():
			photoProp = model.createProperty( PROPERTY.HASPHOTO )
			for photo in self.relatedUrls["photos"]:
				entity.addProperty( photoProp, photo );
			
		# sounds
		if self.hasSound():
			soundProp = model.createProperty( PROPERTY.HASSOUND )
			for sound in self.relatedUrls["sounds"]:
				entity.addProperty( soundProp, sound )
		
		return entity
	
	def parseStatement(self, statement):
		from SmartAPI.model.Address import Address
		from SmartAPI.model.Coordinates import Coordinates
		from SmartAPI.model.Zone import Zone
		from SmartAPI.model.Controllability import Controllability
		from SmartAPI.model.Availability import Availability
		from SmartAPI.model.Activity import Activity
		from SmartAPI.model.Evaluation import Evaluation
		from SmartAPI.model.InterfaceAddress import InterfaceAddress
		from SmartAPI.model.ValueObject import ValueObject
		
		# get predicate
		predicate = str(statement.getPredicate())

		# zone
		if predicate == PROPERTY.ZONE:
			try:
				self.setZone(Zone().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:zone value as resource."
				print sys.exc_info()[1]
				traceback.print_exc()
			return

		# coordinates
		if predicate == PROPERTY.LOCATION:
			try:
				self.setCoordinates(Coordinates().parse(statement.getResource()))
			except:
				print "Unable to interpret geo:location value as resource."
				print sys.exc_info()[1]
				traceback.print_exc()
			return

			# coordinates
		if predicate == PROPERTY.HASADDRESS:
			try:
				self.setAddress(Address().parse(statement.getResource()))
			except:
				print "Unable to interpret vcard:hasAddress value as resource."
				print sys.exc_info()[1]
				traceback.print_exc()
			return
		
		if predicate == PROPERTY.ISMANAGEDBY:
			try:
				self.setManagedBy(Entity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:isManagedBy value as resource."
				print sys.exc_info()[1]
				traceback.print_exc()
			return

		# controllability
		if predicate == PROPERTY.HASEVALUATION:
			try:
				self.addControllability(Controllability().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasEvaluation value as resource."
				traceback.print_exc()
			return

		# availability
		if predicate == PROPERTY.HASAVAILABILITY:
			try:
				self.addAvailability(Availability().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasAvailability value as resource."
				traceback.print_exc()
			return

		# data availability
		if predicate == PROPERTY.HASDATAAVAILABILITY:
			try:
				self.addDataAvailability(Availability().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasDataAvailability value as resource."
				traceback.print_exc()
			return

		# hascapability
		if predicate == PROPERTY.HASCAPABILITY:
			try:
				self.addCapability(Activity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasCapability value as resource."
				traceback.print_exc()
			return
		
		# hascapability
		if predicate == PROPERTY.MANAGES:
			try:
				self.addManagedEntity(Entity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasCapability value as resource."
				traceback.print_exc()
			return
		
		# capacity
		if predicate == PROPERTY.CAPACITY:
			try:
				self.addCapacity(Evaluation().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:capacity value as resource."
				traceback.print_exc() 
			return

		# interfaceaddress
		if predicate == PROPERTY.INTERFACE:
			try:
				self.addInterface(InterfaceAddress().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:interface value as resource."
				traceback.print_exc() 
			return
		
		# creators
		if predicate == PROPERTY.CREATOR:
			try:
				self.addCreator(Entity().parse(statement.getResource()))
			except:
				print "Unable to interpret dc:creator value as resource."
				traceback.print_exc()
			return 
		
		# owner
		if predicate == PROPERTY.OWNER:
			try:
				self.addOwner(Entity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:owner value as resource."
				traceback.print_exc() 
			return
		
			# website
	 	if predicate == PROPERTY.HASURL:
			try:
				self.addWebsite(statement.getString());
			except:
				print "Unable to interpret vcard:hasURL value as string literal."
				traceback.print_exc() 
			return
		
		# logo
		if predicate == PROPERTY.HASLOGO:
			try:
				self.addLogo(statement.getString());
			except:
				print "Unable to interpret vcard:hasLogo value as string literal."
				traceback.print_exc()
			return
		
		# photo
		if predicate == PROPERTY.HASPHOTO:
			try:
				self.addPhoto(statement.getString());
			except:
				print "Unable to interpret vcard:hasPhoto value as string literal."
				traceback.print_exc()
			return
		
		# sound
		if predicate == PROPERTY.HASSOUND:
			try:
				self.addSound(statement.getString());
			except:
				print "Unable to interpret vcard:hasSound value as string literal."
				traceback.print_exc()
			return
		
		# valueobject
		if predicate == PROPERTY.VALUEOBJECT:
			try:
				self.addValueObject(ValueObject().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:valueObject value as resource."
				traceback.print_exc()
			return
		
		# pass on to Object
		super(Entity, self).parseStatement(statement)

	
	def hasZone(self):
		return self.zone is not None
	
	def getZone(self):
		return self.zone

	def setZone(self, zone):
		self.zone = zone

	def hasCoordinates(self):
		return (self.coordinates is not None)
	
	def getCoordinates(self):
		return self.coordinates

	def setCoordinates(self, c):
		self.coordinates = c
	
	def hasAddress(self):
		return (self.address is not None)
	
	def getAddress(self):
		return self.address

	def setAddress(self, a):
		self.address = a

	def hasControllability(self):
		return len(self.controllabilities) > 0
	
	def getControllabilities(self):
		return self.controllabilities
	
	def addControllability(self, controllability):
		self.controllabilities.append(controllability)

	def hasAvailability(self):
		return len(self.availabilities) > 0
	
	def getAvailabilities(self):
		return self.availabilities
	
	def addAvailability(self, availability):
		self.availabilities.append(availability)

	def hasDataAvailability(self):
		return len(self.dataAvailabilities) > 0
	
	def getDataAvailabilities(self):
		return self.dataAvailabilities
	
	def addDataAvailability(self, availability):
		self.dataAvailabilities.append(availability)

	def hasCapability(self):
		return len(self.capabilities) > 0

	def setCapabilities(self, capabilities):
		self.capabilities = capabilities

	def addCapability(self, capability):
		'''
		@param capability: either Activity object, or URI string 
		'''
		from SmartAPI.model.Activity import Activity
		
		if isinstance(capability, Activity):
			self.capabilities.append(capability)
		elif isinstance(capability, str):
			activity = Activity(capability)
			activity.clearTypes()
			self.capabilities.append(activity)

	def getCapabilities(self):
		return self.capabilities

	def hasCapacities(self):
		return len(self.capacities) > 0

	def getCapacities(self):
		return self.capacities
	
	def addCapacity(self, cap):
		self.capacities.append(cap)
	
	def hasManagedEntity(self):
		return len(self.managedEntities) > 0
	
	def getManagedEntities(self):
		return self.managedEntities

	def setManagedEntity(self, e):
		self.managedEntities = []
		self.managedEntities.append(e)
		
	def addManagedEntity(self, e):
		self.managedEntities.append(e)
	
	def hasManagedBy(self):
		return self.managedBy is not None
	
	def setManagedBy(self, obj):
		if isinstance(obj, Obj):
			self.managedBy = obj
		else:
			self.managedBy = Obj(obj)
		
	def getManagedBy(self):
		return self.managedBy
	
	def hasInterface(self):
		return len(self.interfaces) > 0
		
	def getInterfaces(self):
		return self.interfaces

	def setInterface(self, interfaceAddress):
		self.interfaces = [interfaceAddress]

	def addInterface(self, interfaceAddress):
		self.interfaces.append(interfaceAddress)
		
	def hasOwner(self):
		return len(self.owners) > 0
		
	def getOwners(self):
		return self.owners

	def setOwner(self, o):
		self.owners = [o]

	def addOwner(self, o):
		self.owners.append(o)
	
	def hasCreator(self):
		return len(self.creators) > 0
		
	def getCreators(self):
		return self.creators

	def setCreator(self, c):
		self.creators = [c]

	def addCreator(self, c):
		self.creators.append(c)
		

	def hasPhoto(self):
		return self.relatedUrls.has_key("photos");
	
	def getPhotos(self):
		if self.hasPhoto(): return self.relatedUrls["photos"]
		return []
	
	def addPhoto(self, url):
		list = []
		if self.hasPhoto(): 	list = self.getPhotos()
		list.append(url)
		self.relatedUrls["photos"] = list
		
	def hasLogo(self):
		return self.relatedUrls.has_key("logos");
	
	def getLogos(self):
		if self.hasLogo(): return self.relatedUrls["logos"]
		return []
	
	def addLogo(self, url):
		list = []
		if self.hasLogo(): 	list = self.getLogos()
		list.append(url)
		self.relatedUrls["logos"] = list
		
	def hasWebsite(self):
		return self.relatedUrls.has_key("siteurls");
	
	def getWebsites(self):
		if self.hasWebsite(): return self.relatedUrls["siteurls"]
		return []
	
	def addWebsite(self, url):
		list = []
		if self.hasWebsite(): 	list = self.getWebsites()
		list.append(url)
		self.relatedUrls["siteurls"] = list
	
	def hasSound(self):
		return self.relatedUrls.has_key("sounds");
	
	def getSounds(self):
		if self.hasSound(): return self.relatedUrls["sounds"]
		return []
	
	def addSound(self, url):
		list = []
		if self.hasSound(): 	list = self.getSounds()
		list.append(url)
		self.relatedUrls["sounds"] = list
	
	def hasValueObject(self):
		return len(self.valueObjects) > 0
	
	def setValueObjects(self, valueObjects):
		self.valueObjects = valueObjects

	def addValueObject(self, valueObject):
		self.valueObjects.append(valueObject)

	def getValueObjects(self):
		return self.valueObjects
	
	def newValueObject(self, quantity, unit, dataType, description, types):
		'''
		@param types: a list of string, or one single string representing Type; 
		all the others are string types  
		'''
		from SmartAPI.model.ValueObject import ValueObject
		
		valueObject = ValueObject(quantity=quantity, unit=unit, dataType=dataType, 
								description=description, types=types)
		self.addValueObject(valueObject)
		return valueObject
	
	def getValueObjectByQuantity(self, quantity):
		'''
		@type quantity: string 
		'''
		if quantity is not None:
			for vo in self.getValueObjects():
				if vo.hasQuantity() and vo.getQuantity() == quantity:
					return vo
		else:
			for v in self.getValueObjects():
				if not v.hasQuantity():
					return v
				
	def getValueObjectByIdentifier(self, identifier):
		'''
		@type identifier: URI string 
		'''
		if identifier is None or identifier=='':
			return None
		else:
			for vo in self.getValueObjects():
				if vo.hasIdentifierUri(identifier):
					return vo
			return None
