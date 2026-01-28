from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.model.Coordinates import Coordinates

from SmartAPI.common.Tools import Tools

from rdflib import XSD
import traceback

class Orientation(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.yaw = None
		self.pitch = None
		self.roll = None
		self.setType(RESOURCE.ORIENTATION);
	
	def hasYaw(self):
		return self.yaw is not None
	
	def setYaw(self, l):
		self.yaw = l
	
	def getYaw(self):
		return self.yaw
	
	def hasPitch(self):
		return self.pitch is not None
	
	def setPitch(self, l):
		self.pitch = l
	
	def getPitch(self):
		return self.pitch
	
	def hasRoll(self):
		return self.roll is not None
	
	def setRoll(self, a):
		self.roll = a
	
	def getRoll(self):
		return self.roll
		
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
							
		
		orientation = super(Orientation, self).serialize(model)
		
		if self.hasPitch():
			orientation.addProperty(model.createProperty( PROPERTY.PITCH ), self.getPitch().serialize(model))

		if self.hasYaw():
			orientation.addProperty(model.createProperty( PROPERTY.YAW ), self.getYaw().serialize(model))

		if self.hasRoll():
			orientation.addProperty(model.createProperty( PROPERTY.ROLL ), self.getRoll().serialize(model))

		return orientation
	
	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# pitch
			if predicate == PROPERTY.PITCH:
				try:
					self.setPitch(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:pitch value as literal double."
					traceback.print_exc()
				return
	
			# yaw
			if predicate == PROPERTY.YAW:
				try:
					self.setYaw(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:yaw value as literal double."
					traceback.print_exc()
				return
			
			# roll
			if predicate == PROPERTY.ROLL:
				try:
					self.setRoll(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:roll value as literal double."
					traceback.print_exc()
				return
				
			# pass on to Object
			super(Orientation, self).parseStatement(statement)
	