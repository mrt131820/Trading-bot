from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.ValueObject import ValueObject
from SmartAPI.rdf.Variant import Variant
from SmartAPI.common.Tools import Tools

from rdflib import URIRef
import traceback


class Capacity(ValueObject):

	def __init__(self, uri = None, quantity = None, unit = None, value = None, maximum = None, system_of_interest = None):
		ValueObject.__init__(self, uri = uri, quantity = quantity, unit = unit, value = value, maximum = maximum)
		self.automatic_percentage_calculation = True
		self.system_of_interest = system_of_interest
		self.percentage = None
		self.setType(RESOURCE.CAPACITY)
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)	
		
		capacity = super(Capacity, self).serialize(model)
		
		# percentage
		if self.automatic_percentage_calculation:
			self.calculatePercentage()
		if self.hasPercentage():
			capacity.addProperty(model.createProperty( PROPERTY.PERCENTAGE ), self.percentage.serialize(model))

		# systemOfInterest
		if self.hasSystemOfInterest():
			capacity.addProperty(model.createProperty( PROPERTY.SYSTEMOFINTEREST ), self.system_of_interest.serialize(model))
		
		return capacity
	
	
	def parseStatement(self, statement):
		from SmartAPI.model.SystemOfInterest import SystemOfInterest
		from SmartAPI.rdf.Variant import Variant
		from SmartAPI.rdf.Resource import Resource
	
		# get predicate
		predicate = str(statement.getPredicate())
		
		# percentage
		if predicate == PROPERTY.PERCENTAGE:
			try:
				self.setPercentage(Variant().parse(statement))
			except:
				print "Unable to interpret seas:percentage value as resource."
				traceback.print_exc() 
			return

		# systemofInterest
		if predicate == PROPERTY.SYSTEMOFINTEREST:
			try:
				self.setSystemOfInterest(SystemOfInterest().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:systemOfInterest value as resource."
				traceback.print_exc() 
			return
		
		# pass on to ValueObject
		super(Capacity, self).parseStatement(statement)

	def hasPercentage(self):
		return self.percentage is not None

	def getPercentage(self):
		return self.percentage
	
	def getPercentageAsInteger(self):
		try:
			return self.percentage.getValue()
		except:
			return None
	
	def getPercentageAsDouble(self):
		try:
			return self.percentage.getValue()
		except:
			return None
		
	def setPercentage(self, p):
		self.percentage = p

	def hasSystemOfInterest(self):
		return self.system_of_interest is not None

	def getSystemOfInterest(self):
		return self.system_of_interest
	
	def setSystemOfInterest(self, s):
		self.system_of_interest = s

	def enableAutomaticPercentageCalculation(self):
		automatic_percentage_calculation = True
		
	def disableAutomaticPercentageCalculation(self):
		automatic_percentage_calculation = False
		
	def calculatePercentage(self):
		if self.hasValue() and self.hasMaximum():
			v = self.value.getValue()
			m = self.maximum.getValue()
			if v is not None and m is not None:
				if m != 0:							
					self.setPercentage(Variant(v/m*100))
					return True
		return False
