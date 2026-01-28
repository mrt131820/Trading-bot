from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY

from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Message import Message
from SmartAPI.smartapiexceptions.NonePointerException import NonePointerException

import traceback

class Response(Message):
	
	def __init__(self, uri = None):
		Message.__init__(self, uri)
		self.setType(RESOURCE.RESPONSE)

	
	@classmethod
	def fromString(cls, data, serialization):
		from SmartAPI.common.Tools import Tools
		try:
			return cls.parse(Tools().getResourceByType(RESOURCE.RESPONSE, Tools().fromString(data, serialization)))
		except:
			print "Unable to parse Response from the given string."
			traceback.print_exc() 
			return None
	
	
