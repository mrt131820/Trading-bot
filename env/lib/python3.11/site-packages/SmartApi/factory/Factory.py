from SmartAPI.rdf.Model import Model
import traceback
import sys
import datetime
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.smartapiexceptions.NonePointerException import NonePointerException

class Factory(object):

	defaultIdentity = "http://unknown.smartapi.partner"	
	def __init__(self):
		pass
	
	def createModel(self):
		return Model()

	def createValueObject(self, name = None, unit = None, quantity = None, description = None, datatype = None):
		from SmartAPI.model.ValueObject import ValueObject
		from SmartAPI.rdf.Variant import Variant

		vo = None
		try:
			vo = ValueObject()
			if name is not None:			vo.setName(name)
			if quantity is not None:		vo.setQuantity(quantity)
			if unit is not None:			vo.setUnit(unit)
			if description is not None:		vo.setDescription(description)
			if datatype is not None:		vo.setValue(Variant(datatype))
		except:
			print "Exception while creating a ValueObject"
			print sys.exc_info()[1]
			vo = None
		return vo
	
	"""
	 Set all namespaces declared in given class (e.g. NS) to the model.
	 @param model the model where namespaces are added
	 @param klazz class containing the namespaces as attributes
	"""
	def setNameSpaces(self, model, klazz):
		try:
			fields = klazz.getDeclaredFields();
			for field in fields:
				model.setNsPrefix(field.getName().toLowerCase(), field.get(klazz).toString())
		except:
			traceback.print_exc()
			
	@classmethod
	def createTransaction(cls, transactionIdentifierUri, generatedBy):
		'''
		return a newly generated Transaction Object 
		'''
		from SmartAPI.model.Transaction import Transaction
		from SmartAPI.model.Activity import Activity
		from SmartAPI.smartapiexceptions.InsufficientDataException import InsufficientDataException
		
		transaction = Transaction(transactionIdentifierUri)
		if generatedBy is None:
			raise InsufficientDataException
		
		transaction.setGeneratedBy(Activity(generatedBy))
		transaction.getGeneratedBy().clearTypes()
		
		# timestamp of when this message is being generated (now)
		transaction.setGeneratedAt(datetime.datetime.now())

		return transaction
		
	@classmethod
	def createDuration(cls, years, months, days, hours, minutes, seconds):
		'''
		All 6 parameters are integers.
		@return: a newly created isodate Duration Object
		'''
		from isodate.duration import Duration	
		return Duration(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
	
	@classmethod
	def _createStandardActivity(cls, identifier, interfaceAddress, methodUri, temporalContext, timeSeries, valueObjects):
		'''
		@type identifier, methodUri: string; 
		@type valueObjects: a list of ValueObjects.
		others are object 
		'''
		from SmartAPI.model.Activity import Activity
		from SmartAPI.model.Entity import Entity
		
		if identifier is not None:
			a = Activity(identifier)
		else:
			a = Activity()
		a.setMethod(methodUri)
		e = Entity()
		if valueObjects is not None:
			for vo in valueObjects:
				e.addValueObject(vo)
		
		a.addEntity(e)
		if interfaceAddress is not None:
			a.addInterface(interfaceAddress)
		if temporalContext is not None:
			a.setTemporalContext(temporalContext)
		if timeSeries is not None:
			a.addTimeSerie(timeSeries)
		
		return a
	
	@classmethod
	def createStandardReadActivity(cls, identifier=None, interfaceAddress=None, valueObjects=None):
		return cls._createStandardActivity(identifier, interfaceAddress, RESOURCE.READ, None, None, valueObjects)
	
	@classmethod
	def createStandardWriteActivity(cls, identifier=None, interfaceAddress=None, valueObjects=None):	
		return cls._createStandardActivity(identifier, interfaceAddress, RESOURCE.WRITE, None, None, valueObjects)	
	
	@classmethod
	def createStandardReadTimeSeriesActivity(cls, identifier=None, interfaceAddress=None, valueObjects=None):
		from SmartAPI.model.TimeSeries import TimeSeries
		return cls._createStandardActivity(identifier, interfaceAddress, RESOURCE.READ, None, TimeSeries(), valueObjects)
	
	@classmethod
	def createStandardWriteTimeSeriesActivity(cls, identifier=None, interfaceAddress=None, valueObjects=None):
		from SmartAPI.model.TimeSeries import TimeSeries
		return cls._createStandardActivity(identifier, interfaceAddress, RESOURCE.WRITE, None, TimeSeries(), valueObjects)
	
	@classmethod
	def createStandardInterface(cls, domain):
		'''
		@param domain string 
		'''	
		from SmartAPI.model.InterfaceAddress import InterfaceAddress
		
		ia = InterfaceAddress()
		if (domain is None) or (domain == ""):
			domain = cls.defaultIdentity
		
		port = 80
		try:
			if "://" in domain:
				domain = domain.split("://")[1]
			if "/" in domain:
				domain = domain.split("/")[0]
			if ":" in domain:
				parts = domain.split(":")
				domain = parts[0]	
				port = parts[1]
		except:
			traceback.print_exc()
			
		if domain is not None and domain != "":
			ia.setHost(domain)
		
		ia.setPath("/smartapi/v1.0e1.0/access/")
		ia.setPort(port)
		ia.setScheme("http")
		return ia
	
	@classmethod
	def createInterface(cls, uri):
		from SmartAPI.model.InterfaceAddress import InterfaceAddress
		
		if uri is None or uri == "":
			return cls.createStandardInterface(None)
		
		ia = InterfaceAddress()
		try:
			parts = uri.split("://")
			ia.setScheme(parts[0])
			
			if "/" in parts[1]:
				# parts[1] contains both host and path
				items = parts[1].split('/', 1)
				ia.setPath('/' + items[1])
				if ':' in items[0]:
					# items[0] has host + port 
					host, port = items[0].split(':')
					ia.setHost(host)
					ia.setPort(port)
				else:
					# items[0] has no port
					ia.setHost(items[0])
			else: # parts[1] has only host, no path				
				if ':' in parts[1]:
					# the host has also port
					host, port = parts[1].split(':')
					ia.setHost(host)
					ia.setPort(port)
				else:
					# no port
					ia.setHost(parts[1])
			return ia
		
		except:
			return ia
		
	@classmethod
	def createRequest(cls, key, method, senderIdentity, entity, temporalContext, timeSeries, *valueObjects):
		from SmartAPI.factory.RequestFactory import RequestFactory
		from SmartAPI.model.Request import Request
		from SmartAPI.model.Activity import Activity
		from SmartAPI.model.Entity import Entity
		from SmartAPI.model.ValueObject import ValueObject
		
		if (senderIdentity is None) or (senderIdentity == ""):
			senderIdentity = cls.defaultIdentity
		r = RequestFactory().create(senderIdentity)
		
		if entity is None:
			raise NonePointerException("Cannot create read request for null Entity.")
		
		# TODO should actually search for possible activity identifier uri in object.valueobject.capabilities
		a = Activity()
		r.addActivity(a)
		if key is not None:
			a.encrypt(key)
		
		a.setMethod(method)
		
# 		if entity.hasIdentifierUri():
# 			e = Entity(entity.getIdentifierUri())
# 		else:
# 			e = Entity()	
		e = entity
		e.setValueObjects([])	
		
		if temporalContext is not None:
			a.setTemporalContext(temporalContext)
		
		if timeSeries is not None:
			a.addTimeSerie(timeSeries)
		
		a.addEntity(e)
		
		if (valueObjects is None or len(valueObjects) == 0) and method == RESOURCE.WRITE:
			valueObjects = entity.getValueObjects()
		
		if valueObjects is not None:
			for v in valueObjects:
#  				vo = ValueObject(quantity = v.getQuantity(), unit = v.getUnit(), dataType = v.getDataType(), description = v.getDescription())
#  				if v.hasIdentifierUri():
#  					vo.setIdentifierUri(v.getIdentifierUri())
#  				if method == RESOURCE.WRITE:
#  					vo.setValue(v.getValue())
# 				e.addValueObject(vo)
				e.addValueObject(v)
		
		return r
	
	@classmethod
	def createReadRequest(cls, senderIdentity, entity, temporalContext=None, *valueObjects):
		return cls.createRequest(None, RESOURCE.READ, senderIdentity, entity, temporalContext, None, *valueObjects)	
	
	@classmethod
	def createEncryptedReadRequest(cls, senderIdentity, key, entity, temporalContext=None, *valueObjects):
		return cls.createRequest(key, RESOURCE.READ, senderIdentity, entity, temporalContext, None, *valueObjects)
	
	@classmethod
	def createWriteRequest(cls, senderIdentity, entity, timeSeries=None, *valueObjects):
		return cls.createRequest(None, RESOURCE.WRITE, senderIdentity, entity, None, timeSeries, *valueObjects) 
	
	@classmethod
	def createEncryptedWriteRequest(cls, senderIdentity, key, entity, timeSeries=None, *valueObjects):
		return cls.createRequest(key, RESOURCE.WRITE, senderIdentity, entity, None, timeSeries, *valueObjects)

