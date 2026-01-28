from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.types import *

from SmartAPI.common.Tools import Tools

from rdflib import XSD
import traceback

class InterfaceAddress(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.host = None
		self.port = None
		self.path = None
		self.scheme = None
		self.contentTypes = []
		self.setType(RESOURCE.INTERFACEADDRESS);
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		interfaceAddress = super(InterfaceAddress, self).serialize(model)
		
		# host
		if self.hasHost():
			interfaceAddress.addProperty(model.createProperty( PROPERTY.HOST ), model.createTypedLiteral(self.host, XSD.string))

		# port
		if self.hasPort():
			interfaceAddress.addProperty(model.createProperty( PROPERTY.PORT ), model.createTypedLiteral(self.port, XSD.integer))

		# path
		if self.hasPath():
			interfaceAddress.addProperty(model.createProperty( PROPERTY.PATH ), model.createTypedLiteral(self.path, XSD.string))

		# scheme
		if self.hasScheme():
			interfaceAddress.addProperty(model.createProperty( PROPERTY.SCHEME ), model.createTypedLiteral(self.scheme, XSD.string))

		# content types
		for cType in self.contentTypes:
			interfaceAddress.addProperty(model.createProperty( PROPERTY.CONTENTTYPE ), model.createTypedLiteral(cType, XSD.string))

		return interfaceAddress

	
	def parseStatement(self, statement):
		
		# get predicate
		predicate = str(statement.getPredicate())

		# scheme
		if predicate == PROPERTY.SCHEME:
			try :
				self.scheme = statement.getString();
			except:
				print "Unable to interpret seas:scheme value as literal string."
				traceback.print_exc()
		
		# host
		if predicate == PROPERTY.HOST:
			try :
				self.host = statement.getString();
			except:
				print "Unable to interpret seas:host value as literal string."
				traceback.print_exc()

		# port
		if predicate == PROPERTY.PORT:
			try:
				self.port = statement.getInt();
			except:
				print "Unable to interpret seas:port value as literal integer."
				traceback.print_exc()

		# path
		if predicate == PROPERTY.PATH:
			try:
				self.path = statement.getString()
			except:
				print"Unable to interpret seas:path value as literal string."
				traceback.print_exc()

		# content-type
		if predicate == PROPERTY.CONTENTTYPE:
			try:
				self.addContentType(statement.getString())
			except:
				print"Unable to interpret seas:contentType value as literal string."
				traceback.print_exc()

		# pass on to Object
		super(InterfaceAddress, self).parseStatement(statement)
	
		
	
	def hasHost(self):
		return self.host is not None
	
	def setHost(self, host):
		self.host = host
	
	def getHost(self):
		return self.host
	
	def hasPort(self):
		return self.port is not None

	def setPort(self, port):
		self.port = port
	
	def getPort(self):
		return self.port
	
	def hasPath(self):
		return self.path is not None

	def setPath(self, path):
		self.path = path
	
	def getPath(self):
		return self.path
	
	def hasScheme(self):
		return self.scheme != None

	def setScheme(self, scheme):
		self.scheme = scheme
	
	def getScheme(self):
		return self.scheme
	
	def hasContentType(self):
		return len(self.contentTypes) > 0
	
	def setContentType(self, type):
		self.contentTypes = [type]
	
	def addContentType(self, type):
		self.contentTypes.append(type)
	
	def getContentType(self):
		return self.contentTypes
	
	def getInterfaceUri(self):
		uri = ''
		if self.hasScheme():
			uri = self.getScheme() + '://'
		if self.hasHost():
			uri = uri + self.getHost()
		if self.hasPort() and self.getPort() != 80:
			uri = uri + ":" + str(self.getPort())
		if self.hasPath():
			if self.getPath().startswith('/'):
				uri = uri + self.getPath()
			else:
				uri = uri + '/' + self.getPath()
			
		return uri	
