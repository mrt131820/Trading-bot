from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.common.Tools import Tools

from rdflib import XSD
import traceback

class Direction(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.bearing = None
		self.heading = None
		self.tracking = None
		self.course = None
		self.setType(RESOURCE.DIRECTION);
	
	def hasHeading(self):
		return self.heading is not None
	
	def setHeading(self, l):
		self.heading = l
	
	def getHeading(self):
		return self.heading
	
	def hasBearing(self):
		return self.bearing is not None
	
	def setBearing(self, l):
		self.bearing = l
	
	def getBearing(self):
		return self.bearing
	
	def hasTracking(self):
		return self.tracking is not None
	
	def setTracking(self, a):
		self.tracking = a
	
	def getTracking(self):
		return self.tracking
	
	def hasCourse(self):
		return self.course is not None
	
	def setCourse(self, a):
		self.course = a
	
	def getCourse(self):
		return self.course
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		direction = super(Direction, self).serialize(model)
		
		if self.hasBearing():
			direction.addProperty(model.createProperty( PROPERTY.BEARING ), self.getBearing().serialize(model))

		if self.hasHeading():
			direction.addProperty(model.createProperty( PROPERTY.HEADING ), self.getHeading().serialize(model))

		if self.hasTracking():
			direction.addProperty(model.createProperty( PROPERTY.TRACKING ), self.getTracking().serialize(model))

		if self.hasCourse():
			direction.addProperty(model.createProperty( PROPERTY.COURSE ), self.getCourse().serialize(model))

		return direction
	
	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# bearing
			if predicate == PROPERTY.BEARING:
				try:
					self.setBearing(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:bearing value as ValueObject."
					traceback.print_exc()
				return
	
			# heading
			if predicate == PROPERTY.HEADING:
				try:
					self.setHeading(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:heading value as ValueObject."
					traceback.print_exc()
				return
			
			# tracking
			if predicate == PROPERTY.TRACKING:
				try:
					self.setTracking(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:tracking value as ValueObject."
					traceback.print_exc()
				return
	
				# tracking
			if predicate == PROPERTY.COURSE:
				try:
					self.setCourse(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:course value as ValueObject."
					traceback.print_exc()
				return
			
			# pass on to Object
			super(Direction, self).parseStatement(statement)
	