from SmartAPI.model.Evaluation import Evaluation
from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.Statement import Statement
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.Tools import Tools

import traceback

class Input(Evaluation):
	TYPE_DATA = 0
	TYPE_REFERENCE = 1
		
	def __init__(self, uri = None, inputType = 0):
		Evaluation.__init__(self, uri)
		self.inputType = inputType
		self.outputValues = []
		self.setType(RESOURCE.INPUT)
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		input = super(Input, self).serialize(model)
		
		# outputs
		for ov in self.outputValues:
			input.addProperty(model.createProperty( PROPERTY.OUTPUTVALUES ), ov.serialize(model))
			
		return input

	def parseStatement(self, statement):
		from SmartAPI.model.ValueObject import ValueObject
				
		predicate = str(statement.getPredicate())
		
		# output vals
		if  predicate == PROPERTY.OUTPUTVALUES:
			try:
				self.addOutputValue(ValueObject().parse(statement.getResource()));
			except:
				print "Unable to interpret seas:outputValues value as resource."
				traceback.print_exc()
			return

		super(Input, self).parseStatement(statement)

	def getInputType(self):
		return self.inputType
	
	def setInputType(self, inputType):
		self.inputType = inputType

	def hasOutputValue(self):
		return len(self.outputValues) > 0

	def getOutputValues(self):
		return self.outputValues
	
	def setOutputValue(self, ov):
		self.outputValues = [ov]

	def addOutputValue(self, ov):
		self.outputValues.append(ov)
	
