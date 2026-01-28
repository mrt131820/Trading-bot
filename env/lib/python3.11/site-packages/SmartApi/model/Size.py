from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Obj import Obj
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.common.Tools import Tools

from rdflib import XSD
import traceback

class Size(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.height = None
		self.width = None
		self.depth = None
		self.setType(RESOURCE.SIZE);
	
	def hasHeight(self):
		return self.height is not None
	
	def setHeight(self, l):
		self.height = l
	
	def getHeight(self):
		return self.height
	
	def hasWidth(self):
		return self.width is not None
	
	def setWidth(self, l):
		self.width = l
	
	def getWidth(self):
		return self.width
	
	def hasDepth(self):
		return self.depth is not None
	
	def setDepth(self, a):
		self.depth = a
	
	def getDepth(self):
		return self.depth
		
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		size = super(Size, self).serialize(model)
		
		if self.hasWidth():
			size.addProperty(model.createProperty( PROPERTY.WIDTH ), self.getWidth().serialize(model))

		if self.hasHeight():
			size.addProperty(model.createProperty( PROPERTY.HEIGHT ), self.getHeight().serialize(model))

		if self.hasDepth():
			size.addProperty(model.createProperty( PROPERTY.DEPTH ), self.getDepth().serialize(model))

		return size
	
	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# width
			if predicate == PROPERTY.WIDTH:
				try:
					self.setWidth(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:width value as literal double."
					traceback.print_exc()
				return
	
			# height
			if predicate == PROPERTY.HEIGHT:
				try:
					self.setHeight(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:height value as literal double."
					traceback.print_exc()
				return
			
			# depth
			if predicate == PROPERTY.DEPTH:
				try:
					self.setDepth(ValueObject().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:depth value as literal double."
					traceback.print_exc()
				return
				
			# pass on to Object
			super(Size, self).parseStatement(statement)
	