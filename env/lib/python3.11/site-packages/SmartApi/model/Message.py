from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY

from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Evaluation import Evaluation
from SmartAPI.model.Error import Error
from SmartAPI.model.Status import Status
from SmartAPI.common.Tools import Tools

from SmartAPI.smartapiexceptions.NonePointerException import NonePointerException

import sys
from rdflib import URIRef, XSD
import traceback

class Message(Evaluation):
	
	def __init__(self, uri = None):
		Evaluation.__init__(self, uri)
		self.messageId = -1
		self.processId = -1
		self.status = None
		self.method = None
		self.errors = []
		self.setType(RESOURCE.MESSAGE)
		
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)	
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
				
		resource = super(Message, self).serialize(model)
		
		# errors
		errorProp = model.createProperty( PROPERTY.ERROR )
		for e in self.errors:
			errorRes = e.serialize(model);
			resource.addProperty( errorProp, errorRes )
		
		# status
		if self.hasStatus():
			resource.addProperty(model.createProperty( PROPERTY.STATUS ), self.getStatus().serialize(model))

		if self.hasMessageId():
			resource.addProperty(model.createProperty( PROPERTY.ID ), model.createTypedLiteral(self.getMessageId(), XSD.integer))

		if self.hasProcessId():
			resource.addProperty(model.createProperty( PROPERTY.PROCESSID ), model.createTypedLiteral(self.getProcessId(), XSD.integer))

		if self.hasMethod():
			resource.addProperty(model.createProperty( PROPERTY.METHOD ), self.getMethod())
		
		return resource
	
	def parseStatement(self, statement):
		from SmartAPI.model.Error import Error
		# get predicate
		predicate = str(statement.getPredicate())
		
		# status
		if predicate == PROPERTY.ID:
			try:
				self.messageId = statement.getInt()
			except:
				print "Unable to interpret seas:messageId value."
				traceback.print_exc() 
			return

		# status
		if predicate == PROPERTY.PROCESSID:
			try:
				self.processId = statement.getInt()
			except:
				print "Unable to interpret seas:processId value."
				traceback.print_exc() 
			return
		
		# status
		if predicate == PROPERTY.STATUS:
			try:
				self.status = Status().parse(statement.getResource())
			except:
				print "Unable to interpret seas:status value as resource."
				traceback.print_exc() 
			return
		
		# errors
		if predicate == PROPERTY.ERROR:
			try:
				self.addError(Error().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:error value as resource."
				traceback.print_exc() 
			return

		# status
		if predicate == PROPERTY.METHOD:
			try:
				self.method = URIRef(statement.toString())
			except:
				print "Unable to interpret seas:method value."
				print sys.exc_info()[1]
				traceback.print_exc() 
			return
		
		# pass on to Evaluation
		super(Message, self).parseStatement(statement)

	def hasMethod(self):
		return self.method is not None
	
	def getMethod(self):
		return self.method
	
	def setMethod(self, m):
		if not isinstance(m, URIRef): m = URIRef(m)
		self.method = m
		
	def hasMessageId(self):
		return self.messageId > -1
	
	def getMessageId(self):
		return self.messageId
	
	def setMessageId(self, _messageId):
		self.messageId = _messageId
		
	def hasProcessId(self):
		return self.processId > -1
	
	def getProcessId(self):
		return self.processId
	
	def setProcessId(self, _processId):
		self.processId = _processId
	
	def setStatus(self, s):
		self.status = s

	def getStatus(self):
		return self.status
	
	def hasStatus(self):
		return self.status is not None

	def addError(self, e):
		self.errors.append(e)

	def getErrors(self):
		return self.errors
	
	def hasErrors(self):
		return len(self.errors) > 0

