from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Evaluation import Evaluation
from SmartAPI.common.Tools import Tools

import traceback

class Output(Evaluation):

	def __init__(self, uri = None):
		Evaluation.__init__(self, uri)
		self.availabilities = []
		self.dataAvailabilities = []
		self.setType(RESOURCE.OUTPUT)
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
							
		
		output = super(Output, self).serialize(model)
		
		# availability
		availabilityProp = model.createProperty( PROPERTY.HASAVAILABILITY )
		for availability in self.availabilities:
			output.addProperty( availabilityProp, availability.serialize(model) )

		# data availability
		dataAvailabilityProp = model.createProperty( PROPERTY.HASDATAAVAILABILITY )
		for availability in self.dataAvailabilities:
			output.addProperty( dataAvailabilityProp, availability.serialize(model) )

		return output


	def parseStatement(self, statement):
		from SmartAPI.model.Availability import Availability
		
		# get predicate
		predicate = str(statement.getPredicate())

		# availability
		if predicate == PROPERTY.HASAVAILABILITY:
			try:
				self.addAvailability(Availability().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasAvailability value as resource."
				traceback.print_exc()
			return

		# data availability
		if predicate == PROPERTY.HASDATAAVAILABILITY:
			try:
				self.addDataAvailability(Availability().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasDataAvailability value as resource."
				traceback.print_exc()
			return

		# pass on to Evaluation
		super(Output, self).parseStatement(statement)

	def hasAvailability(self):
		return len(self.availabilities) > 0
	
	def getAvailabilities(self):
		return self.availabilities
	
	def addAvailability(self, availability):
		self.availabilities.add(availability)

	def hasDataAvailability(self):
		return len(self.dataAvailabilities) > 0
	
	def getDataAvailabilities(self):
		return self.dataAvailabilities
	
	def addDataAvailability(self, availability):
		self.dataAvailabilities.add(availability)

