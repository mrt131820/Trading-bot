from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools
from SmartAPI.rdf.Resource import Resource
from SmartAPI.model.Response import Response

import traceback


class AliveResponse(Response):
	
	def __init__(self, uri = None):
		Response.__init__(self, uri)
		self.setType(RESOURCE.ALIVERESPONSE)
	
	@classmethod
	def fromString(cls, data, serialization):
		try:
			return cls.parse(Tools().getResourceByType(RESOURCE.ALIVERESPONSE, Tools().fromString(data, serialization)))
 		except:
			print "Unable to parse AliveResponse from the given string."
			traceback.print_exc() 
			return None
	
	
		
	

