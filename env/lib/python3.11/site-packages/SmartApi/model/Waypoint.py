from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj
from SmartAPI.model.Coordinates import Coordinates
from SmartAPI.model.Address import Address
from SmartAPI.model.Route import Route
from SmartAPI.rdf.Variant import Variant
from SmartAPI.common.Tools import Tools

import datetime
from dateutil import parser

class Waypoint(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.setType(RESOURCE.WAYPOINT);
		self.coordinates = None
		self.address = None
		self.instant = None
		self.route = None
		
	def hasLocation(self):
		return self.coordinates is not None
	
	def getLocation(self):
		return self.coordinates

	def setLocation(self, coordinates):
		self.coordinates = coordinates

	def hasAddress(self):
		return self.address is not None
	
	def getAddress(self):
		return self.address

	def setAddress(self, address):
		self.address = address

	def hasInstant(self):
		return self.instant is not None
	
	def getInstant(self):
		return self.instant

	def setInstant(self, instant):
		self.instant = Variant(instant)

	def hasRoute(self):
		return self.route is not None
	
	def getRoute(self):
		return self.route
	
	def setRoute(self, route):
		self.route = route
	
		
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		waypoint = super(Waypoint, self).serialize(model)
			
		if self.hasLocation():
			waypoint.addProperty(model.createProperty( PROPERTY.LOCATION ), self.getLocation().serialize(model))
		
		if self.hasAddress():
			waypoint.addProperty(model.createProperty( PROPERTY.HASADDRESS ), self.getAddress().serialize(model))

		if self.hasInstant():
			waypoint.addProperty(model.createProperty( PROPERTY.INSTANT ), model.createLiteral(self.getInstant().getValue()))
		
		if self.hasRoute():
			waypoint.addProperty(model.createProperty( PROPERTY.ROUTE ), self.getRoute().serialize(model))
		
		return waypoint
	
	def parseStatement(self, statement):
		
			predicate = str(statement.getPredicate())

			# coordinates
			if predicate == PROPERTY.LOCATION:
				self.setLocation(Coordinates().parse(statement.getResource()))
				return
			
			# address
			if predicate == PROPERTY.HASADDRESS:
				self.setLocation(Coordinates().parse(statement.getResource()))
				return
			
			# instant
			if predicate == PROPERTY.INSTANT:
				e = statement.getObject().toPython()
				if not isinstance(e, datetime.datetime):
					e = parser.parse(e)
				self.setInstant(e)
				return
			
			# location
			if predicate == PROPERTY.ROUTE:
				self.setRoute(Route().parse(statement.getResource()))
				return
			
			# pass on to Object
			super(Waypoint, self).parseStatement(statement)
		
