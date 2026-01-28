from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools
from SmartAPI.rdf.Resource import Resource

from SmartAPI.model.Request import Request


class AliveRequest(Request):
	
	def __init__(self, uri = None):
		Request.__init__(self, uri)
		self.setType(RESOURCE.ALIVEREQUEST)		
	
	
	
	
		
	@classmethod
	def fromString(cls, data, serialization):
		m = Tools().fromString(data, serialization)
		res = Tools().getResourceByType(RESOURCE.ALIVEREQUEST, m)
		return cls.parse(res)
		