from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.Resource import Resource
from SmartAPI.common.Tools import Tools

from rdflib import XSD

import traceback


class Coordinates(Obj):
	
	def __init__(self, uri = None, latitude = None, longitude = None, altitude = None):
		Obj.__init__(self, uri)
		self.latitude = latitude
		self.longitude = longitude
		self.altitude = altitude
		self.setType(RESOURCE.GEO_POINT);
	
	def hasLongitude(self):
		return self.longitude is not None
	
	def setLongitude(self, l):
		self.longitude = l
	
	def getLongitude(self):
		return self.longitude
	
	def hasLatitude(self):
		return self.latitude is not None
	
	def setLatitude(self, l):
		self.latitude = l
	
	def getLatitude(self):
		return self.latitude
	
	def hasAltitude(self):
		return self.altitude is not None
	
	def setAltitude(self, a):
		self.altitude = a
	
	def getAltitude(self):
		return self.altitude
	
	def toNude(self):
		return ( self.latitude, self.longitude )
	
	def fromNude(self, value):
		self.latitude = value[0]
		self.longitude = value[1]
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
				
		coordinates = super(Coordinates, self).serialize(model)
		
		if self.hasLatitude():
			coordinates.addProperty(model.createProperty( PROPERTY.LAT ), model.createTypedLiteral(self.getLatitude(), XSD.double))

		if self.hasLongitude():
			coordinates.addProperty(model.createProperty( PROPERTY.LONG ), model.createTypedLiteral(self.getLongitude(), XSD.double))

		if self.hasAltitude():
			coordinates.addProperty(model.createProperty( PROPERTY.ALT ), model.createTypedLiteral(self.getAltitude(), XSD.double))

		return coordinates
	
	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
			
			# latitude
			if predicate == PROPERTY.LAT:
				try:
					self.setLatitude(statement.getDouble())
				except:
					print "Unable to interpret geo:lat value as literal double."
					traceback.print_exc()
				return
	
			# longitude
			if predicate == PROPERTY.LONG:
				try:
					self.setLongitude(statement.getDouble());
				except:
					print "Unable to interpret geo:long value as literal double."
					traceback.print_exc()
				return
			
			# altitude
			if predicate == PROPERTY.ALT:
				try:
					self.setAltitude(statement.getDouble());
				except:
					print "Unable to interpret geo:alt value as literal double."
					traceback.print_exc()
				return
	
			# pass on to Object
			super(Coordinates, self).parseStatement(statement)
	
