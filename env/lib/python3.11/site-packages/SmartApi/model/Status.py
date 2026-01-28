from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.Variant import Variant
from SmartAPI.model.TemporalContext import TemporalContext

from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.Statement import Statement
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools
from rdflib import XSD

class Status(Obj):
		
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.setType(RESOURCE.STATUS);
		self.percentage = None
		self.total = None
		self.completed = None
		self.temporalContext = None
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		resource = super(Status, self).serialize(model)
		
		# percentage
		if self.hasPercentage():
			resource.addProperty(model.createProperty(PROPERTY.PERCENTAGE), self.percentage.serialize(model))

		# total
		if self.hasTotal():
			resource.addProperty(model.createProperty(PROPERTY.TOTAL), model.createTypedLiteral(self.total, XSD.int))
	
		# completed
		if self.hasCompleted():
			resource.addProperty(model.createProperty(PROPERTY.COMPLETED), model.createTypedLiteral(self.completed, XSD.int))

		# temporalcontext
		if self.hasTemporalContext():
			resource.addProperty(model.createProperty(PROPERTY.TEMPORALCONTEXT), self.temporalContext.serialize(model))

		return resource

	def parseStatement(self, statement):
		
			predicate = str(statement.getPredicate())
	
			# percentage
			if predicate == PROPERTY.PERCENTAGE:
				self.setPercentage(Variant().parse(statement))
				return

			# total
			if predicate == PROPERTY.TOTAL:
				self.setTotal(statement.getInt())
				return

			# completed
			if predicate == PROPERTY.COMPLETED:
				self.setCompleted(statement.getInt())
				return

			# temporalcontext
			if predicate == PROPERTY.TEMPORALCONTEXT:
				self.setTemporalContext(TemporalContext().parse(statement.getResource()))
				return

			# pass on to Obj
			super(Status, self).parseStatement(statement)

	
	def setPercentage(self, p):
		if not isinstance(p, Variant):
			self.percentage = Variant(p)
		else:
			self.percentage = p
			
	def setTotal(self, t):
		self.total = t
	
	def setCompleted(self, c):
		self.completed = c
	
	def setTemporalContext(self, t):
		self.temporalContext = t
	
	def getPercentage(self):
		return self.percentage
	
	def getTotal(self):
		return self.total
	
	def getCompleted(self):
		return self.completed
	
	def getTemporalContext(self):
		return self.temporalContext
		
	def hasPercentage(self):
		return self.percentage is not None
	
	def hasTotal(self):
		return self.total is not None
	
	def hasCompleted(self):
		return self.completed is not None
	
	def hasTemporalContext(self):
		return self.temporalContext is not None

	def getPercentageAsInteger(self):
		return int(self.percentage)

	def getPercentageAsDouble(self):
		return float(self.percentage)
