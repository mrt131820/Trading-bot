from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.Variant import Variant
from SmartAPI.common.Tools import Tools
from SmartAPI.common.NS import NS
from rdflib import URIRef
import traceback


class ValueObject(Obj):

	def __init__(self, uri = None, quantity = None, unit = None, value = None, 
				dataType = None, description = None, types = None):
		'''
		@param dataType, description, uri, quantity, unit: string 
		@param types: a list of string, or one single string representing Type
		'''
		Obj.__init__(self, uri)
# 		if quantity is not None and not isinstance(quantity, URIRef): quantity = URIRef(quantity)
# 		if unit is not None and not isinstance(unit, URIRef): unit = URIRef(unit)
# 		if value is not None and not isinstance(value, Variant): value = Variant(value)
# 		if dataType is not None and not isinstance(dataType, URIRef): dataType = URIRef(dataType)
		
		self.quantity = quantity
		self.unit = unit		
		self.setValue(value)
		self.maximum = None
		self.minimum = None
		self.setType(RESOURCE.VALUEOBJECT)
		self.temporalContext = None
		self.dataType = dataType
		self.instant = None
		
		if description is not None:
			self.setDescription(description)
		
		if types is not None:
			if isinstance(types, list):
				for ty in types:
					self.addType(ty)
			else:
				self.addType(types)
					

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		valueObject = super(ValueObject, self).serialize(model)

		# quantity
		if self.hasQuantity():
 			quantity = model.createResource(self.quantity)
			valueObject.addProperty(model.createProperty( PROPERTY.QUANTITYKIND ), quantity)
		
		# unit
		if self.hasUnit():
 			unit = model.createResource(self.unit)
			valueObject.addProperty(model.createProperty( PROPERTY.UNIT ), unit)

		# dataType
		if self.hasDataType():
			dataType = model.createResource(self.dataType)
			valueObject.addProperty(model.createProperty( PROPERTY.DATATYPE ), dataType)

		# value
		if self.hasValue():
			valueObject.addProperty(model.createProperty( PROPERTY.RDF_VALUE ), self.value.serialize(model))
			
		if self.hasMaximum():
			valueObject.addProperty(model.createProperty( PROPERTY.MAXIMUM ), self.maximum.serialize(model))
		
		if self.hasMinimum():
			valueObject.addProperty(model.createProperty( PROPERTY.MINIMUM ), self.minimum.serialize(model))
						
		# temporalContext
		if self.hasTemporalContext():
			valueObject.addProperty(model.createProperty(PROPERTY.TEMPORALCONTEXT), self.temporalContext.serialize(model))
		
		# instant
		if self.hasInstant():
			valueObject.addProperty(model.createProperty( PROPERTY.INSTANT ), model.createLiteral(self.instant))				
		
		return valueObject
	
	
	def parseStatement(self, statement):
		from SmartAPI.rdf.Resource import Resource
		from SmartAPI.model.TemporalContext import TemporalContext
	
		# get predicate
		predicate = str(statement.getPredicate())
		
		# quantity
		if predicate == PROPERTY.QUANTITYKIND:
			try:
				self.setQuantity(statement.getResource().toString());
			except:
				print "Unable to interpret seas:quantity value as resource."
				traceback.print_exc() 
			return

		# unit
		if predicate == PROPERTY.UNIT:
			try:
				self.setUnit(statement.getResource().toString())
			except:
				print "Unable to interpret seas:unit value as resource."
				traceback.print_exc() 
			return
		
		# dataType
		if predicate == PROPERTY.DATATYPE:
			try:
				self.setDataType(statement.getResource().toString())
			except:
				print "Unable to interpret seas:dataType value as resource."
				traceback.print_exc() 
			return
		
		# value
		if predicate == PROPERTY.RDF_VALUE:
			self.setValue(Variant().parse(statement))
			return
			
		if predicate == PROPERTY.MAXIMUM:
			self.setMaximum(Variant().parse(statement))
			return
			
		if predicate == PROPERTY.MINIMUM:
			self.setMinimum(Variant().parse(statement))
			return		
		
		# temporalcontext
		if predicate == PROPERTY.TEMPORALCONTEXT:
			try:
				self.setTemporalContext(TemporalContext().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:temporalContext value as resource."
				traceback.print_exc()
			return
				
		# instant
		if predicate == PROPERTY.INSTANT:
			try:
				self.setInstant(statement.getObject().toPython())
			except:
				print "Unable to interpret seas:instant value as date literal."
				traceback.print_exc()
			return
		
		# pass on to Obj
		super(ValueObject, self).parseStatement(statement)
		

	def hasQuantity(self):
		return self.quantity is not None

	def getQuantity(self):
		return self.quantity
	
	def setQuantity(self, quantity):
		'''
		@type quantity: string. It can look like "asema:SomeCustomType" or an URI
		'''
		if quantity is not None:
			quantity = NS.toAbsoluteUri(quantity)
			Tools.handleConceptValidation(quantity)
			self.quantity = quantity	

	def hasUnit(self):
		return self.unit is not None

	def getUnit(self):
		return self.unit
	
	def setUnit(self, unit):
		'''
		@type unit: string. It can look like "asema:SomeCustomType" or an URI
		'''
		if unit is not None:
			unit = NS.toAbsoluteUri(unit)
			Tools.handleConceptValidation(unit)			
			self.unit = unit	

	def hasDataType(self):
		return self.dataType is not None
	
	def getDataType(self):
		return self.dataType
	
	def setDataType(self, dataType):
		'''
		@type dataType: string. It can look like "asema:SomeCustomType" or an URI
		'''
		if dataType is not None:
			dataType = NS.toAbsoluteUri(dataType)
			Tools.handleConceptValidation(dataType)
			self.dataType = dataType		

	def hasValue(self):
		return self.value is not None
	
	def getValue(self):
		return self.value

	def setValue(self, value):
		if value is not None and not isinstance(value, Variant):
			value = Variant(value)
		self.value = value
		
	def hasMaximum(self):
		return self.maximum is not None
	
	def getMaximum(self):
		return self.maximum
	
	def setMaximum(self, max):
		if not isinstance(max, Variant):
			max = Variant(max)
		self.maximum = max
		
	def hasMinimum(self):
		return self.minimum is not None
	
	def getMinimum(self):
		return self.minimum
	
	def setMinimum(self, min):
		if not isinstance(min, Variant):
			min = Variant(min)
		self.minimum = min				

	def getTemporalContext(self):
		return self.temporalContext
	
	def hasTemporalContext(self):
		return self.temporalContext is not None
	
	def setTemporalContext(self, *args):
		'''
		@param args: one Temporalcontext object, 
		or one or two datetime.date, datetime.time or datetime.datetime type values 
		'''
		from SmartAPI.model.TemporalContext import TemporalContext
		
		if len(args) == 1: 
			if isinstance(args[0], TemporalContext):
				self.temporalContext = args[0]
			else:
				self.temporalContext = TemporalContext(start=args[0])
		elif len(args) == 2:
			self.temporalContext = TemporalContext(start=args[0], end=args[1])
			
	def hasInstant(self):
		return self.instant is not None
	
	def getInstant(self):
		return self.instant

	def setInstant(self, instant):
		self.instant = instant	
	