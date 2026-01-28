from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.common.Tools import Tools
from rdflib import XSD

import traceback

class Velocity(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.linearVelocityX = None
		self.linearVelocityY = None
		self.linearVelocityZ = None
		self.angularVelocityX = None
		self.angularVelocityY = None
		self.angularVelocityZ = None
		self.groundSpeed = None
	
		self.setType(RESOURCE.VELOCITY)
	
	def hasLinearVelocityX(self):
		return self.linearVelocityX is not None
	
	def setLinearVelocityX(self, l):
		self.linearVelocityX = l
	
	def getLinearVelocityX(self):
		return self.linearVelocityX
	
	def hasLinearVelocityY(self):
		return self.linearVelocityY is not None
	
	def setLinearVelocityY(self, l):
		self.linearVelocityY = l
	
	def getLinearVelocityY(self):
		return self.linearVelocityY
	
	def hasLinearVelocityZ(self):
		return self.linearVelocityZ is not None
	
	def setLinearVelocityZ(self, l):
		self.linearVelocityZ = l
	
	def getLinearVelocityZ(self):
		return self.linearVelocityZ
	
	def hasAngularVelocityX(self):
		return self.angularVelocityX is not None
	
	def setAngularVelocityX(self, l):
		self.angularVelocityX = l
	
	def getAngularVelocityX(self):
		return self.angularVelocityX

	def hasAngularVelocityY(self):
		return self.angularVelocityY is not None
	
	def setAngularVelocityY(self, l):
		self.angularVelocityY = l
	
	def getAngularVelocityY(self):
		return self.angularVelocityY
	
	def hasAngularVelocityZ(self):
		return self.angularVelocityZ is not None
	
	def setAngularVelocityZ(self, l):
		self.angularVelocityZ = l
	
	def getAngularVelocityZ(self):
		return self.angularVelocityZ
		
	def hasGroundSpeed(self):
		return self.groundSpeed is not None
	
	def setGroundSpeed(self, a):
		self.groundSpeed = a
	
	def getGroundSpeed(self):
		return self.groundSpeed
		
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		speed = super(Velocity, self).serialize(model)
		
		if self.hasAngularVelocityX():
			speed.addProperty(model.createProperty( PROPERTY.ANGULARVELOCITYX ), self.getAngularVelocityX().serialize(model))
		if self.hasAngularVelocityY():
			speed.addProperty(model.createProperty( PROPERTY.ANGULARVELOCITYY ), self.getAngularVelocityY().serialize(model))
		if self.hasAngularVelocityZ():
			speed.addProperty(model.createProperty( PROPERTY.ANGULARVELOCITYZ ), self.getAngularVelocityZ().serialize(model))

		if self.hasLinearVelocityX():
			speed.addProperty(model.createProperty( PROPERTY.LINEARVELOCITYX ), self.getLinearVelocityX().serialize(model))
		if self.hasLinearVelocityY():
			speed.addProperty(model.createProperty( PROPERTY.LINEARVELOCITYY ), self.getLinearVelocityY().serialize(model))
		if self.hasLinearVelocityZ():
			speed.addProperty(model.createProperty( PROPERTY.LINEARVELOCITYZ ), self.getLinearVelocityZ().serialize(model))

		if self.hasGroundSpeed():
			speed.addProperty(model.createProperty( PROPERTY.GROUNDSPEED ), self.getGroundSpeed().serialize(model))

		return speed
	
	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# angularVelocityX
			if predicate == PROPERTY.ANGULARVELOCITYX:
				try:
					self.setAngularVelocityX(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:angularVelocityX value as literal double."
					traceback.print_exc()
				return
			
			# angularVelocityY
			if predicate == PROPERTY.ANGULARVELOCITYY:
				try:
					self.setAngularVelocityY(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:angularVelocityY value as literal double."
					traceback.print_exc()
				return
			
			# angularVelocityZ
			if predicate == PROPERTY.ANGULARVELOCITYZ:
				try:
					self.setAngularVelocityZ(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:angularVelocityZ value as literal double."
					traceback.print_exc()
				return
				
			# linearVelocityX
			if predicate == PROPERTY.LINEARVELOCITYX:
				try:
					self.setLinearVelocityX(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:linearVelocityX value as literal double."
					traceback.print_exc()
				return
			
			# linearVelocityY
			if predicate == PROPERTY.LINEARVELOCITYY:
				try:
					self.setLinearVelocityY(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:linearVelocityY value as literal double."
					traceback.print_exc()
				return
			
			# linearVelocityZ
			if predicate == PROPERTY.LINEARVELOCITYZ:
				try:
					self.setLinearVelocityZ(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:linearVelocityZ value as literal double."
					traceback.print_exc()
				return
			# groundSpeedX
			if predicate == PROPERTY.GROUNDSPEED:
				try:
					self.setGroundSpeed(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:groundSpeed value as literal double."
					traceback.print_exc()
				return
				
			# pass on to Object
			super(Velocity, self).parseStatement(statement)
	
