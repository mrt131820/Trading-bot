from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.Tools import Tools
from SmartAPI.rdf.Resource import Resource

from SmartAPI.model.Obj import Obj
from SmartAPI.model.Input import Input

import traceback


class Activity(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.setType(RESOURCE.ACTIVITY)
		self.inputs = []
		self.outputs = []
		self.availabilities = []
		self.dataAvailabilities = []
		self.interfaces = []
		self.entities = []
		self.temporalContext = None
		self.timeSeries = []
		self.method = None

	def serialize(self, model):
		from SmartAPI.common.Tools import Tools
		
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		activity = super(Activity, self).serialize(model)
		# inputs
		for input in self.inputs:
			if input.getInputType() == Input.TYPE_DATA:
				activity.addProperty(model.createProperty( PROPERTY.HASINPUT ), input.serialize(model))
			if input.getInputType() == Input.TYPE_REFERENCE:
				activity.addProperty(model.createProperty( PROPERTY.HASREFINPUT ), input.serialize(model))	

		# outputs
		for output in self.outputs:
			activity.addProperty(model.createProperty( PROPERTY.HASOUTPUT ), output.serialize(model))
	
		# availability
		availabilityProp = model.createProperty( PROPERTY.HASAVAILABILITY )
		for availability in self.availabilities:
			activity.addProperty( availabilityProp, availability.serialize(model) )

		# data availability
		dataAvailabilityProp = model.createProperty( PROPERTY.HASDATAAVAILABILITY )
		for availability in self.dataAvailabilities:
			activity.addProperty( dataAvailabilityProp, availability.serialize(model) )

		# set interfaces
		for iAddrs in self.interfaces:
			activity.addProperty(model.createProperty( PROPERTY.INTERFACE ), iAddrs.serialize(model))
		
		# entities
		for entity in self.entities:
			activity.addProperty( model.createProperty( PROPERTY.ENTITY ), entity.serialize(model) )

		# temporalcontext
		if self.hasTemporalContext():
			activity.addProperty(model.createProperty( PROPERTY.TEMPORALCONTEXT ), self.temporalContext.serialize(model))
		
		# timeseries
		for timeSerie in self.timeSeries:
			activity.addProperty( model.createProperty( PROPERTY.TIMESERIES ), timeSerie.serialize(model) )
			
		# method
		if self.hasMethod():
			methodProp = model.createProperty( PROPERTY.METHOD )
			activity.addProperty( methodProp, model.createResource(self.getMethod()) )

		return activity
	

	def parseStatement(self, statement):
		from SmartAPI.model.Availability import Availability
		from SmartAPI.model.Input import Input
		from SmartAPI.model.Output import Output
		from SmartAPI.model.InterfaceAddress import InterfaceAddress
		from SmartAPI.model.Entity import Entity
		from SmartAPI.model.TimeSeries import TimeSeries
		from SmartAPI.model.TemporalContext import TemporalContext
					
		predicate = str(statement.getPredicate())

		# method
		if predicate == PROPERTY.METHOD:
			try:
				self.setMethod(statement.getResource().toString())
			except:
				print "Unable to interpret smartapi:method value as literal string."
				traceback.print_exc()
			return
		
		# input data
		if predicate == PROPERTY.HASINPUT:
			try:
				self.addInput(Input.parse(statement.getResource()))
			except:
				print "Unable to interpret smartapi:hasInput value as resource."
				traceback.print_exc()
			return

		# input reference
		if predicate == PROPERTY.HASREFINPUT:
			try:
				input = Input.parse(statement.getResource())
				input.setInputType(Input.TYPE_REFERENCE)
				self.addInput(input)
			except:
				print "Unable to interpret smartapi:hasRefInput value as resource."
				traceback.print_exc()
			return

		# output
		if  predicate == PROPERTY.HASOUTPUT:
			try:
				self.addOutput(Output.parse(statement.getResource()));
			except:
				print "Unable to interpret smartapi:hasOutput value as resource."
				traceback.print_exc()
			return

		# availability
		if predicate == PROPERTY.HASAVAILABILITY:
			try:
				self.addAvailability(Availability.parse(statement.getResource()))
			except:
				print "Unable to interpret smartapi:hasAvailability value as resource."
				traceback.print_exc()
			return

		# data availability
		if predicate == PROPERTY.HASDATAAVAILABILITY:
			try:
				self.addDataAvailability(Availability.parse(statement.getResource()))
			except:
				print "Unable to interpret smartapi:hasDataAvailability value as resource."
				traceback.print_exc()
			return

		# interfaceaddress
		if predicate == PROPERTY.INTERFACE:
			try:
				self.addInterface(InterfaceAddress.parse(statement.getResource()))
			except:
				print "Unable to interpret smartapi:interface value as resource."
				traceback.print_exc()
			return
		
		# entity
		if predicate == PROPERTY.ENTITY:
			try:
				self.addEntity(Tools.fromResourceAsObj(statement.getResource()))
			except:
				print "Unable to interpret smartapi:entity value (of type smartapi:Entity) as resource."
				traceback.print_exc()
			return

		# temporalcontext
		if predicate == PROPERTY.TEMPORALCONTEXT:
			try:
				self.setTemporalContext(TemporalContext().parse(statement.getResource()))
			except:
				print "Unable to interpret smartapi:temporalContext value as resource."
				traceback.print_exc()
			return
		
		# timeserie
		if predicate == PROPERTY.TIMESERIES:
			try:
				self.addTimeSerie(TimeSeries().parse(statement.getResource()))
			except:
				print "Unable to interpret smartapi:timeSeries value as resource."
				traceback.print_exc()
			return
		
		# pass on to Object
		super(Activity, self).parseStatement(statement)


	def hasInput(self):
		return len(self.inputs) > 0

	def getInputs(self):
		return self.inputs
	
	def setInput(self, input):
		self.inputs = [input]

	def addInput(self, input):
		self.inputs.append(input)

	def hasOutput(self):
		return len(self.outputs) > 0

	def getOutputs(self):
		return self.outputs
	
	def setOutput(self, output):
		self.outputs = [output]

	def addOutput(self, output):
		self.outputs.append(output)

	def hasAvailability(self):
		return len(self.availabilities) > 0
	
	def getAvailabilities(self):
		return self.availabilities
	
	def addAvailability(self, availability):
		self.availabilities.append(availability)

	def hasDataAvailability(self):
		return len(self.dataAvailabilities) > 0
	
	def getDataAvailabilities(self):
		return self.dataAvailabilities
	
	def addDataAvailability(self, availability):
		self.dataAvailabilities.append(availability)

	def getInterfaces(self):
		return self.interfaces;
	
	def getHTTPInterface(self):
		for ia in self.getInterfaces():
			if ia.hasScheme() and (ia.getScheme().lower() == 'http'):
				return ia
	
	def setInterface(self, interfaceAddress):
		self.interfaces = [interfaceAddress]

	def addInterface(self, interfaceAddress):
		self.interfaces.append(interfaceAddress)
		
	def hasEntity(self):
		return len(self.entities) > 0

	def setEntities(self, entities):
		'''
		@param entities: a list of Entity objects 
		'''
		self.entities = entities

	def addEntity(self, entity):
		self.entities.append(entity)

	def getEntities(self):
		return self.entities
	
	def getEntity(self, identifierUri):
		for entity in self.entities:
			if identifierUri == entity.getIdentifierUri():
				return entity
		return None

	def firstInput(self):
		try:
			return self.inputs[0]
		except:
			return None
    
	def firstOutput(self):
		try:
			return self.outputs[0]
		except:
			return None
	
	def hasMethod(self):
		return self.method is not None
	
	def getMethod(self):
		return self.method
	
	def setMethod(self, methodUri):
		'''
		@param methodUri: method Uri string
		'''	
		self.method = methodUri
	
	def hasTemporalContext(self):
		return self.temporalContext is not None

	def getTemporalContext(self):
		return self.temporalContext

	def setTemporalContext(self, temporalContext):
		self.temporalContext = temporalContext
		
	def hasTimeSeries(self):
		return len(self.timeSeries) > 0
	
	def getTimeSeries(self):
		return self.timeSeries
		
	def addTimeSerie(self, timeSerie):
		self.timeSeries.append(timeSerie)
		