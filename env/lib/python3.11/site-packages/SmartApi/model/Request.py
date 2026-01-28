from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY

from SmartAPI.model.Message import Message
from SmartAPI.rdf.Resource import Resource
from SmartAPI.smartapiexceptions.NonePointerException import NonePointerException

import traceback
import sys
from rdflib import URIRef

class Request(Message):

	def __init__(self, uri = None):
		Message.__init__(self, uri)
		self.setType(RESOURCE.REQUEST)
		
	
	@classmethod
	def fromString(cls, data, serialization):
		from SmartAPI.common.Tools import Tools		
		try:
			return cls.parse(Tools().getResourceByType(RESOURCE.REQUEST, Tools().fromString(data, serialization)));
		except:
			print "Unable to parse Request from the given string."
			traceback.print_exc() 
			return None
	
	
