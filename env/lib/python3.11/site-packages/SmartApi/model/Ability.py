from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from Evaluation import Evaluation
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Condition import Condition
from SmartAPI.common.Tools import Tools

import traceback

class Ability(Evaluation):

	def __init__(self, uri = None):
		Evaluation.__init__(self, uri)
		self.isControlledBy = None
		self.condition = None
		self.setType(RESOURCE.ABILITY)
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		resource = super(Ability, self).serialize(model)

		# isControlledBy
		if self.hasIsControlledBy():
			controlledBy = model.createResource(self.isControlledBy)
			resource.addProperty(model.createProperty( PROPERTY.ISCONTROLLEDBY ), controlledBy)

		# condition
		if self.hasCondition():
			resource.addProperty(model.createProperty( PROPERTY.HASCONDITION ), self.condition.serialize(model))

		return resource
	
	def parseStatement(self, statement):
			# get predicate
			predicate = str(statement.getPredicate())
	
			# isControlledBy
			if predicate == PROPERTY.ISCONTROLLEDBY:
				try:
					self.setIsControlledBy(statement.getResource().toString())
				except:
					print "Unable to interpret seas:isControlledBy value as resource."
					traceback.print_exc()
				return
	
			# condition
			if predicate == PROPERTY.HASCONDITION:
				try:
					self.setCondition(Condition.parse(statement.getResource()))
				except:
					print "Unable to interpret seas:hasCondition value as resource."
					traceback.print_exc()
				return
	
			# pass on to Object
			super(Ability, self).parseStatement(statement);

	def hasIsControlledBy(self):
		return self.isControlledBy is not None

	def getIsControlledBy(self):
		return self.isControlledBy;
	
	def setIsControlledBy(self, isControlledBy):
		self.isControlledBy = isControlledBy

	def hasCondition(self):
		return self.condition is not None
	
	def getCondition(self):
		return self.condition;

	def setCondition(self, condition):
		self.condition = condition
