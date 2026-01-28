from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.model.Obj import Obj
from SmartAPI.model.Coordinates import Coordinates
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.common.Tools import Tools
from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.types import *
from rdflib import XSD

import traceback

class Ring(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.minRadius = None
		self.maxRadius = None
		self.coordinates = None
		self.setType(RESOURCE.RING)

	def hasCoordinates(self):
		return self.coordinates is not None
	
	def getCoordinates(self):
		return self.coordinates

	def setCoordinates(self, coordinates):
		self.coordinates = coordinates

	def hasMinRadius(self):
		return self.minRadius is not None
	
	def getMinRadius(self):
		return self.minRadius

	def setMinRadius(self, r):
		self.minRadius = r

	def hasMaxRadius(self):
		return self.maxRadius is not None
	
	def getMaxRadius(self):
		return self.maxRadius

	def setMaxRadius(self, r):
		self.maxRadius = r

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		resource = super(Ring, self).serialize(model)
	
		# coordinates
		if self.hasCoordinates():
			resource.addProperty(model.createProperty( PROPERTY.LOCATION ), self.coordinates.serialize(model))
				
		# min radius
		if self.hasMinRadius():
			resource.addProperty(model.createProperty( PROPERTY.MINRADIUS ), self.minRadius.serialize(model))
		
		# max radius
		if self.hasMaxRadius():
			resource.addProperty(model.createProperty( PROPERTY.MAXRADIUS ), self.maxRadius.serialize(model))
		
		return resource


	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# latitude
			if predicate == PROPERTY.LOCATION:
				try:
					self.setCoordinates(Coordinates().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:coordinates value as coordinates."
					traceback.print_exc()
				return
		
			if predicate == PROPERTY.MINRADIUS:
				try:
					self.setMinRadius(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:minradius value."
					traceback.print_exc()
				return
	
			if predicate == PROPERTY.MAXRADIUS:
				try:
					self.setMaxRadius(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:maxradius value."
					traceback.print_exc()
				return
			
			# pass on to Object
			super(Ring, self).parseStatement(statement)
	
