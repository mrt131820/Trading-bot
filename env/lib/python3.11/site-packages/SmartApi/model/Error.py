from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Obj import Obj
from rdflib.namespace import XSD
from SmartAPI.common.Tools import Tools

class Error(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.message = None
		self.code = 0
		self.setType(RESOURCE.ERROR);
	
	def setErrorMessage(self, em):
		self.message = em
	
	def getErrorMessage(self):
		return self.message
	
	def setErrorCode(self, ec):
		self.code = ec
	
	def getErrorCode(self):
		return self.code
	
	def hasErrorCode(self):
		return self.code > 0
	
	def hasErrorMessage(self):
		return self.message != None
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		error = super(Error, self).serialize(model)
		
		if self.hasErrorMessage():
			error.addProperty(model.createProperty( PROPERTY.ERRORMESSAGE ), model.createTypedLiteral(self.getErrorMessage(), XSD.string))
		
		if self.hasErrorCode():
			error.addProperty(model.createProperty( PROPERTY.ERRORCODE ), model.createTypedLiteral(self.getErrorCode(), XSD.integer))
		
		return error
	
	def parseStatement(self, statement):
		# get predicate
		predicate = str(statement.getPredicate())
		
		# err message
		if predicate == PROPERTY.ERRORMESSAGE:
			self.setErrorMessage(statement.getResource().toString())
			return

		# err code
		if predicate == PROPERTY.ERRORCODE:
			self.setErrorCode(int(statement.getResource().toString()))
			return

		# pass on to Object
		super(Error, self).parseStatement(statement)
	
