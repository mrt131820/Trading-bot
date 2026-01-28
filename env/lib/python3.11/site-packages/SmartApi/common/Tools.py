from SmartAPI.factory.Factory import Factory
from SmartAPI.rdf.Property import Property
from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.LinkedList import LinkedList
from SmartAPI.rdf.OrderedList import OrderedList
from SmartAPI.rdf.ItemizedList import ItemizedList
from SmartAPI.rdf.NudeList import NudeList
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.CONTENTTYPES import CONTENTTYPE
from SmartAPI.common.ClassMapper import ClassMapper
from SmartAPI.common.HttpMessage import HttpMessage
from SmartAPI.common.HttpMessage import HttpMessageSingle
from SmartAPI.common.HttpMessage import parseMIMEmessage
from SmartAPI.common.SERIALIZATION import SERIALIZATION
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.SmartAPICrypto import SmartAPICrypto
from SmartAPI.common.URLs import KEYSERVER_URI
from SmartAPI.common.ValidationMode import ValidationMode

from SmartAPI.smartapiexceptions.NotFoundException import NotFoundException
from rdflib import URIRef
from rdflib.namespace import RDF

import traceback
import datetime
import urllib
from isodate.duration import Duration


class Tools(object):
	# to keep track already serialized Objects, cleared before serialization
	serializedObjs = {}
	# to keep track already parsed Objects, cleared before parse
	parsedObjs = {}
	
	defaultIdentity = "http://unknown.smartapi.partner"	
		
	def __init__(self):
		self.mapper = ClassMapper()
	
	@classmethod
	def createCryptoKeys(cls):
		c = SmartAPICrypto()
		priv, pub = c.generateKeyPair()
		pubStr = c.convertPublicKeyToPemFormat(pub)
		privStr = c.convertPrivateKeyToPemFormat(priv)
		return privStr, pubStr
	
	@classmethod
	def uploadPublicKey(cls, key, identifier, username, password, server = KEYSERVER_URI):
		SmartAPICrypto().uploadPublicKey(key, identifier, server, username, password)
		
	@classmethod
	def revokePublicKey(cls, identifier, username, password, server = KEYSERVER_URI):
		SmartAPICrypto().revokePublicKey(identifier, server, username, password)
		
	@classmethod
	def toString(cls, element, serialization=SERIALIZATION.TURTLE):
		'''
		serialize Seas Obj or its subclass Obj to string. 
		'''				
		cls.serializedObjs.clear()
		
		model = Factory().createModel()
		
		if isinstance(element, list) or isinstance(element, OrderedList) or isinstance(element, ItemizedList) or isinstance(element, NudeList):			
			# Raw top level list. We need some blank node to hold the list
			holder_element = Resource(model = model)
			holder_element.addProperty(Property(RDF.first), element)
			top_element = Resource(model = model)
			top_element.addProperty(Property(PROPERTY.LIST), holder_element)
			cls.addRecursivelyToModel(top_element, model)
			
		elif isinstance(element, LinkedList):
			top_element = Resource(model = model)
			top_element.addProperty(Property(PROPERTY.LIST), element)
			cls.addRecursivelyToModel(top_element, model)
		else:
			cls.addRecursivelyToModel(element, model)
		
		# serialize
		messageBody = ""
		try:
			messageBody = model.serialize(format=serialization)
		except:
			print "Exception while converting model into string"
			traceback.print_exc()
				
		return messageBody

	@classmethod
	def fromString(cls, strng, serialization = None):
		model = Factory().createModel()
		try:
			model.parse(data = strng, format=serialization)
		except:
			print "Could not parse the input into a model"
			traceback.print_exc()
		
		cls.parsedObjs.clear()
		
		return model
	
	def fromFile(self, filename, serialization):
		model = Factory.createModel()

		try:
			f = open(filename)
			model.parse(file = filename, format=serialization)
			f.close()
		except:
			print "Could not read the file into a model"
			traceback.print_exc()
			
		return model
	
	@classmethod
	def fromResourceAsObj(cls, resource, objType = None):
		cm = ClassMapper()
		if objType is None:
			types = cls.getResourceTypes(resource)
		else:
			types = [str(objType)]
		obj = cm.getClass(types)()
		if resource.getId() is not None: obj.setIdentifierUri(resource.getId())
		sl = resource.findProperties()
		for s in sl:
			obj.parseStatement(s)
		return obj
	
	@classmethod
	def fromStringAsObj(cls, strng, serialization = None, isType = None):
		model = self.fromString(strng, serialization = serialization)
		if isType is None:
			node, isType = cls.getTopNode(model)
		
		res = cls.getResourceByType(isType, model)
		return self.fromResourceAsObj(node, objType)
	
	def fromStringAsList(self, strng, serialization = None, isType = None):
		model = self.fromString(strng, serialization = serialization)
		sl = model.listStatements(subject = None, predicate = URIRef(RDF.first), object = None)		
		list_container = []
		# Find the "orphan" rdf.first node, this is the starting point of all lists
		for s in sl:
			ss = model.listStatements(subject = None, predicate = None, object = s.getSubject())
			if len(ss) == 0:
				model.parse_list(list_container, parent_node = s.getSubject(), first = s.getObject())
				break
		
		return list_container
	
	def toObj(self, objStr, serialization = SERIALIZATION.TURTLE):
		'''
		@param objStr: string presentation of Seas Obj. 
		@return: The Obj or its subclass Object
		'''
		model = self.fromString(objStr, serialization)
		rootRes = self.getTopNode(model)[0]
		seasCls = self.getResourceClass(rootRes)
		recoveredObj =  seasCls.parse(rootRes)
		return recoveredObj
		
	def getSerializationForContentType(self, content_type):
		if CONTENTTYPE.mapping.has_key(content_type):
			return CONTENTTYPE.mapping[content_type]
		return "Unknown"
	
	@classmethod
	def addRecursivelyToModel(cls, resource, model):
		from SmartAPI.model.Obj import Obj
		
		# add this level statements
		if isinstance(resource, Obj):
			model.add(resource.serialize(model))
		elif isinstance(resource, list):
			for item in resource:
				cls.addRecursivelyToModel(item, model)
		else:
			model.add(resource)
			
	@classmethod
	def dateToString(cls, date_time):
		"""
	 	Convert Python datetime to xsd:dateTime string
	 	@param dateTime timestamp to convert
	 	@return xsd:dateTime stype string
		"""
		ret = None
		try:
			ret = date_time.strftime("%Y-%m-%dT%H:%M:%S")
		except:
			print "Error while converting zoned datetime to ISO offset datetime string"
		return ret
	
	@classmethod
	def stringToDate(cls, date_str):
		date = None
		try:
			date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
		except:
			print "Error while converting ISO offset datetime string to zoned datetime"
		return date
	
	@classmethod
	def stringToDuration(cls, dur_str):
		'''
		@return isodate.Duration or datetime.timedelta object, depending on whether the dur_str contains
		Months, years, weeks
		'''
		import isodate
		try:
			duration = isodate.parse_duration(dur_str)
			return duration
		except:
			print 'Invalid duration string!'
			return None
	
	@classmethod
	def durationToString(cls, duration):
		import isodate
		'''
		@param duration: either datetime.timedelta or isodate.Duration
		@return string 
		'''
		return isodate.duration_isoformat(duration)
		
	def stripUri(self, uri):
		stripped = uri
		splits = uri.split("#", 1)
		if len(splits) > 1:
			stripped = splits[1]
		return stripped;
	
	@classmethod
	def getResourceByType(cls, type, model):
		return model.findSubject(URIRef(PROPERTY.RDF_TYPE), URIRef(type))

	"""
	def getResourceByType(self, type, model):
		typeResource = model.createResource(type)
		typeProperty = model.createProperty(PROPERTY.RDF_TYPE)

		s = model.listStatements(None, typeProperty, typeResource)
		if len(s) > 0:
			r = Resource(model, s.getSubject())
			return r
		else:
			raise NotFoundException("Could not find resource by type " + type + " from the provided model.")
	"""
	
	def getResourceType(self, resource):
		object = resource.getPropertyResourceValue(resource.getModel().createProperty(PROPERTY.RDF_TYPE))
		if ( object is not None ):
			return object.toString()
		return None

	@classmethod
	def getResourceTypes(cls, resource):
		types = []
		for statement in resource.findProperty(resource.getModel().createProperty(PROPERTY.RDF_TYPE)):
			types.append(statement.getResource().toString())
		return types
	
	def getResourceClass(self, resource, default = None):
		types = self.getResourceTypes(resource)
		return self.mapper.getClass(types, default = default)

	@classmethod
	def createIdentifierUri(cls, myDomain, systemIdentifier, *objectIdentifiers):
		'''
		@return: a URI string
		'''			
		if ( myDomain is None or myDomain == "" ):
			myDomain = cls.defaultIdentity.split("://")[1].split("/")[0]
		
		if myDomain.startswith("http://"):
			result = myDomain
		else:
			result = "http://" + myDomain
			
		if  (systemIdentifier is not None) and (systemIdentifier != ""):
			result += "/"
			result += urllib.quote(systemIdentifier, safe='')
		
		for objId in objectIdentifiers:
			if (objId is not None) and (objId != ""):
				result += "/"
				result += urllib.quote(objId, safe='')
		
		return result

	@classmethod
	def getTopNode(cls, model):
		# Find the top node of a received structure. To do this, find all triples where
		# the subject is not the object of anything.
		# These subjects are the resources of orphan nodes. Because we are eventually
		# looking for the RDF type of the objects, it is enough to iterate the nodes
		# that contain an RDF type attribute
		nodeType = None
		node = None
		sl = model.listStatements(subject = None, predicate = URIRef(PROPERTY.RDF_TYPE), object = None)
		for s in sl:
			nodeType = s.getObject()
			ss = model.listStatements(subject = None, predicate = None, object = s.getSubject())
			if len(ss) == 0:
				id = None if not isinstance(s.getSubject(), URIRef) else str(s.getSubject())
				node = Resource(id = id, model = model, node = s.getSubject())
				break
		if node is not None:
			return node, nodeType
		
		# Nothing found. Probably a loop so just pick some node.
		#if (l.size() == 0 && s.length() > 0) {
		if len(sl) > 0:
			s = sl[0]
			nodeType = s.getObject()
			id = None if not isinstance(s.getSubject(), URIRef) else str(s.getSubject())
			node = Resource(id = id, model = model, node = s.getSubject())
			if nodeType is not None and node is not None:
				return node, nodeType
		raise NotFoundException("Could not find any orphan objects from the provided model.")
	
	@classmethod
	def printErrors(cls, response):
		for error in response.getErrors():
			cls.printError(error)
		
	@classmethod
	def printError(cls, error):
		print '*  ------   ERROR   ------  * \n'
		for typeObj in error.getTypes():
			typeUri = typeObj.getIdentifierUri()
			type = typeUri
			
			if typeUri == RESOURCE.PARSEERROR:
				type = 'parse error'
			elif typeUri == RESOURCE.INVALIDPARAMS:
				type = 'Invalid parameters' 
			elif typeUri == RESOURCE.INVALIDREQUEST:
				type = 'invalide request'
			elif typeUri == RESOURCE.SERVERERROR:
				type = 'server error'
			
			print '* Type:		', type
			print '* Error message: ', error.getErrorMessage()
			print '*  ------   ERROR   ------  *'
	
	@classmethod
	def serializeNotification(cls, message, serialization = 'text/turtle', noHeader=True):
		'''
		'''
		return cls.serializeMessage(message, serialization, noHeader)
		
	
	@classmethod
	def serializeRequest(cls, message, serialization = 'text/turtle', noHeader=True):
		'''
		@see  serializeMessage
		@param message: Request Object
		@param serialization: it has to be MIME media type 
		@param noHeader: true if MIME headers are stripped. useful when sending out through HTTP POST
		'''
		return cls.serializeMessage(message, serialization, noHeader)
	
	@classmethod
	def serializeResponse(cls, message, serialization = 'text/turtle', noHeader=True):
		'''
		@see  serializeMessage
		@param message: Response Object
		@param serialization: it has to be MIME media type 
		@param noHeader: true if MIME headers are stripped, useful when sending out through HTTP POST
		'''
		return cls.serializeMessage(message, serialization, noHeader)
	
	@classmethod
	def serializeMessage(cls, message, serialization = 'text/turtle', noHeader=True):
		'''		 
		Extended version of Tools.toString() method. This method takes a Request or Response Object as input, 
		return MIME message (multipart or single part). 
		
		@param message: Request or Response Object
		@param serialization: it has to be MIME media type 
		@param noHeader: true if MIME headers are stripped, useful when sending out through HTTP POST
		
		@return: two strings, one string is the serialized message with or without MIME headers(i.e., Content-Type header)
		, decided by 'noHeader' parameter
		the other string is the Content-Type header 				
		'''
		Tools.messageParts.clear()
		# this step might add new items to Tools.messageParts.					
		messageString = cls.toString(message, serialization)
		# multipart or single part generation goes here. 		
		if len(Tools.messageParts) == 0:
			httpMessageSingle = HttpMessageSingle()
			httpMessageSingle.add(messageString, serialization)
			messagePayload = httpMessageSingle.asString().replace("\n", "\r\n")
			if noHeader:
				messagePayload = cls._stripMIMEheaders(messagePayload)
			return (messagePayload, httpMessageSingle.getContentType())
		else: # add messageString and additional messageParts into multipart
			httpMessage= HttpMessage()
			httpMessage.addMainpart(messageString, serialization)
			for partId in Tools.messageParts.keys():
				httpMessage.add(partId, Tools.messageParts.get(partId), serialization)
			Tools.messageParts.clear()
			messagePayload = httpMessage.asString().replace("\n", "\r\n")
			if noHeader:
				messagePayload = cls._stripMIMEheaders(messagePayload)
			return (messagePayload, httpMessage.getContentType())
	
	@classmethod
	def _stripMIMEheaders(cls, mimeMsg):
		#import os
		'''
		@param mimeMsg: a MIME message string including MIME headers
		@return: a string stripped of MIME headers
		'''
		return mimeMsg.split("\r\n"+"\r\n", 1)[1]  #(os.linesep+os.linesep, 1)[1]
	
	@classmethod
	def parseNotification(cls, content, content_type = None, serialization='text/turtle'):
		'''
		'''
		from SmartAPI.model.Notification import Notification
		notification = Notification.fromString(content, serialization)
		return notification
	
	@classmethod
	def parseRequest(cls, content, content_type = None, serialization='text/turtle'):
		'''
		Extended version of Request/Response.fromString() method. It can handle both multipart and singlepart.
		
		@param content: message body with Content-Type headers (if content_type is None) as a String.
		@param content_type: if None, the content parameter includes Content-Type headers. 
		@param serialization: it has to be MIME media type
		@return: a Request Object. 
		'''
		from SmartAPI.model.Request import Request
		httpMessage = parseMIMEmessage(content, content_type = content_type)
		msgString = httpMessage.getMainPart()
		if isinstance(httpMessage, HttpMessage): # multipart
			Tools.messagePartsForParse = httpMessage.getNonMainPartsAsDict() 
		
		else: # single part
			Tools.messagePartsForParse = {}
		
		# convert msgString to Response or Request object		
		model = cls.fromString(msgString, serialization)
		msgResource = cls.getResourceByType(RESOURCE.REQUEST, model)
		# This step might consume items from Tools.messagePartsForParse
		return Request.parse(msgResource)
	
	@classmethod
	def parseResponse(cls, content, content_type = None, serialization = "text/turtle"):
		'''
		Extended version of Request/Response.fromString() method. It can handle both multipart and singlepart.
		
		@param content: message body with Content-Type headers (if content_type is None) as a String.
		@param content_type: if None, the content parameter includes Content-Type headers. 
		@param serialization: it has to be MIME media type
		@return: a Response Object. 
		'''
		from SmartAPI.model.Response import Response
		
		httpMessage = parseMIMEmessage(content, content_type = content_type)
		msgString = httpMessage.getMainPart()
		if isinstance(httpMessage, HttpMessage): # multipart
			Tools.messagePartsForParse = httpMessage.getNonMainPartsAsDict()
			
		else: # single part
			Tools.messagePartsForParse = {}
		
		# convert msgString to Response or Request object.		
		model = cls.fromString(msgString, serialization)
		msgResource = cls.getResourceByType(RESOURCE.RESPONSE, model)
		# This step might consume items from Tools.messagePartsForParse
		return Response.parse(msgResource)
		
	messageParts = {} 
	''' A dictionary for keeping non-Main parts. Key is URI of a model class Object, value is
		encrypted string representation of this object.
		Every execution of serializeToReference() from Obj object or its subClass will add one 
		item to this dictionary. It will be cleared at the beginning and at the end of 
		Tools().serializeMessage() method ''' 
	
	@classmethod
	def saveForMessageParts(cls, uri, partString):
		'''
		This method is only used by Obj().serializeToReference() 
		'''
		cls.messageParts[uri] = partString
		
	messagePartsForParse = {} 
	''' Similar as the above 'messageParts' dictionary. 
	It will be filled with items in the middle of Tools.parseRequest() or Tools.parseResponse() method. 
	Every execution of parse() from Obj object or its subClass will consume one item from this dictionary 
	if the URI matches the key.'''
		
	@classmethod
	def getMostCommonActivity(cls, method, withTimeSeries, entity, *valueObjects):
		'''
		@param method: string, either RESOURCE.READ or RESOURCE.WRITE
		@param withTimeSeries: boolean, does the searched activity consider timeseries?
		@param entity: activities shall be searched from this entity
		@param valueObjects: any number of ValueObjects. if present, then only if value objects from that entity share the same quantities as these ValueObjects will be searched
		'''		
		if valueObjects is None or len(valueObjects) == 0:
			valueObjects = entity.getValueObjects()	
					
		#	go through all valueobjects.  <activity, number of occurrences>
		commonActivities = {}
		for v in valueObjects:	
			# 	get equivalent vo from the entity
			vo = entity.getValueObjectByIdentifier(v.getIdentifierUri())
			if vo is None:
				vo = entity.getValueObjectByQuantity(v.getQuantity())
			if vo is None:
				vo = v
			# go through capabilities of the entity							
			for a in entity.getCapabilities():
				# if has required method
				if a.getMethod() == method:
					# if has or not required possible timeserie/tcx
					if method == RESOURCE.READ:
						if (withTimeSeries and a.hasTemporalContext()) or (not withTimeSeries and not a.hasTemporalContext()):
							if cls.supportsThisValueObject(a, vo):
								if a in commonActivities:
									commonActivities[a] += 1
								else:
									commonActivities[a] = 1 
					elif method == RESOURCE.WRITE:
						if (withTimeSeries and a.hasTimeSeries()) or (not withTimeSeries and not a.hasTimeSeries()): 
							if cls.supportsThisValueObject(a, vo):
								if a in commonActivities:
									commonActivities[a] += 1
								else:
									commonActivities[a] = 1
		
		# get one with most matches
		numberOfMatches = 0		
		selectedActivity = None	
		for key, value in commonActivities.iteritems():
			if value > numberOfMatches:
				selectedActivity = key
				numberOfMatches = value
					
		return selectedActivity
	
	@classmethod
	def supportsThisValueObject(cls, activity, valueObject):
		'''
		return true if activity (a) has any entity that has any value objects that has same
	    identifier or same quantity than valueobject (vo)
		'''
		for e in activity.getEntities():
			if e.getValueObjectByIdentifier(valueObject.getIdentifierUri()) is not None:
				return True
			if e.getValueObjectByQuantity(valueObject.getQuantity()) is not None:
				return True
		return False

	@classmethod
	def handleConceptValidation(cls, uri, validation_mode=ValidationMode.NO_VALIDATION):
		from SmartAPI.model.Obj import Obj
		from SmartAPI.common.ConceptDetails import ConceptDetails
		# get the uri's namespace URL
		uri = uri.strip()
		NSstr = Obj.getNSstring(uri)
		
		found = False	
		if validation_mode == ValidationMode.REALTIME_VALIDATION:
			# rely on these downloadable urls hardcoded at ConceptDetails class
			if NSstr in ConceptDetails.coreUrlMap or NSstr in ConceptDetails.customUrlMap:
				if ConceptDetails.coreCustomOntStore is None:
					ConceptDetails.loadCoreCustomOntStore()
				found = ConceptDetails.checkCoreCustomResource(uri)
			else:
				found = ConceptDetails.checkOtherResource(uri, NSstr)
			if not found:
				print 'Invalid concept: ', uri
			
def cleanupConceptDetails():
	'''
	clean up ontology memory resource used by Obj.explain() method. 
	'''
	from SmartAPI.common.ConceptDetails import ConceptDetails
	ConceptDetails.close()	
	
import atexit
atexit.register(cleanupConceptDetails)
