from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.VARIANT import VARIANT
from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.Resource import Resource
from SmartAPI.common.Tools import Tools

from rdflib import Literal, BNode, URIRef, XSD

import datetime
import isodate
from isodate.duration import Duration
import traceback

class Variant(object):

	def __init__(self, value = None):
		self.variant = value
	
	def set(self, value):
		self.variant = value
	
	def serialize(self, model):
		
		if self.isObj() or self.isVariant():
			return self.variant.serialize(model)
		elif self.isDuration():
			return model.createTypedLiteral(isodate.duration_isoformat(self.variant), XSD.duration)
		else:
			return self.asTerm()

	def asTerm(self):
		if self.isUri():
			return self.variant
		elif self.isNull():
			return None
		else:
			return Literal(self.variant)

	def parse(self, statement):
		# get predicate and object
		predicate = str(statement.getPredicate())
		objectNode = statement.getObject()

		# if literal object
		dataType = None
		if isinstance(objectNode, Literal):
			return Variant(objectNode.toPython())
		
		elif (statement.getResource() is not None):
			resource = statement.getResource()
			klass = Tools().getResourceClass(resource, default = Obj)
			if klass is not None:
				v = klass().parse(resource)
			else:
				# None found, resort to Obj (the base class)
				v = Obj().parse(resource)
			
			return v
			
		elif isinstance(objectNode, BNode):
			l = []
			statement.getResource().getModel().parse_list(l, objectNode, None)
			return l
		
		elif isinstance(objectNode, URIRef):
			return Variant(objectNode)
					
		# could not identify datatype
		print "Parsing variant failed. Unable to detect RDFDatatype (" + str(dataType) + ") for literal."
		return Variant("");


	def isNull(self):
		return self.variant is None

	def isUri(self):
		return isinstance(self.variant, URIRef)
	
	def isString(self):
		return isinstance(self.variant, str)
	
	def isInteger(self):
		return isinstance(self.variant, int) or isinstance(self.variant, long)

	def isDouble(self):
		return isinstance(self.variant, float)
		
	def isFloat(self):
		import decimal
		if isinstance(self.variant, decimal.Decimal):
			self.variant = float(self.variant)		
		return isinstance(self.variant, float)

	def isBoolean(self):
		return isinstance(self.variant, bool)

	def isDate(self):
		return isinstance(self.variant, datetime.date)

	def isTime(self):
		return isinstance(self.variant, datetime.time)
	
	def isDateTime(self):
		return isinstance(self.variant, datetime.datetime)
	
	def isDuration(self):
		return (isinstance(self.variant, Duration) or isinstance(self.variant, datetime.timedelta)) 
	
	def isMap(self):
		from SmartAPI.model.Map import Map
		return isinstance(self.variant, Map)
	
	def isObj(self):
		return isinstance(self.variant, Obj)
	
	def isVariant(self):
		return isinstance(self.variant, Variant)

	def getValue(self):
		if isinstance(self.variant, Literal):
			return self.variant.toPython()
		return self.variant

	def getType(self):
		if self.isNull():
			return "Null"
		elif self.isUri():
			return "Uri"
		elif self.isString():
			return "string"
		elif self.isInteger():
			return "int"
		elif self.isDouble():
			return "double"
		elif self.isFloat():
			return "float"
		elif self.isBoolean():
			return "boolean"
		elif self.isDate():
			return "date"
		elif self.isTime():
			return "time"
		elif self.isDateTime():
			return "datetime"
		elif self.isDuration():
			return 'duration'
		elif self.isMap():
			return "Map"
		elif self.isObj():
			return "Obj"
		elif self.isVariant():
			return "Variant"
		else:
			return None

	def getAsString(self):
		return str(self.variant)

	# Most method below have no significance in Python as the language
	# is not strongly typed. They are however offered as convenience
	# to make implementions between different languages as similar
	# as possible
	def asString(self):
		return self.getAsString()
	
	def asObj(self):
		return self.variant

	def asInt(self):
		try:
			return int(self.variant)
		except:
			return 0
		
	def asDouble(self):
		try:
			return float(self.variant)
		except:
			return 0
	
	def asDuration(self):
		'''
		@return a isodate.Duration or datetime.timedelta value if valid, otherwise None
		'''
		if isinstance(self.variant, datetime.timedelta) or isinstance(self.variant, Duration):
			return self.variant
		
	def asFloat(self):
		try:
			return float(self.variant)
		except:
			return 0

	def asBoolean(self):
		return self.variant
		
	def asDate(self):
		try:
			return Tools().stringToDate(str(self.variant)).date()
		except:
			return None
		
	def asTime(self):
		try:
			return Tools().stringToDate(str(self.variant)).time()
		except:
			return None	
	
	def hasSameValue(self, other):
		return self.variant==other.variant
	
	def __repr__(self):
		return "<Variant:: type: %s, value: %s>"%(self.getType(), self.getValue())
	
	
