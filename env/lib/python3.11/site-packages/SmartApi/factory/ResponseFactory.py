from SmartAPI.model.Response import Response
from SmartAPI.model.Activity import Activity
from SmartAPI.common.Tools import Tools
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.smartapiexceptions.InsufficientDataException import InsufficientDataException

import datetime
import traceback

class ResponseFactory(object):

	def __init__(self):
		pass
	
	def create(self, generatedBy):
		resp = Response()
		if (generatedBy is None or (generatedBy is not None and generatedBy == "")):
			raise InsufficientDataException("Invalid seas:generatedBy URI.");
	
		g = Activity(generatedBy)
		g.clearTypes()
		resp.setGeneratedBy(g)
		
		# timestamp of when this message is being generated (now)
		resp.setGeneratedAt(datetime.datetime.now())

		resp.addType(RESOURCE.RESPONSE)
		
		return resp

	
	def fromString(self, data, serialization):
		try :
			return Response().parse(Tools().getResourceByType(RESOURCE.RESPONSE, Tools().fromString(data, serialization)));
		except:
			print "Unable to parse Response by type seas:Response from the given string."
			traceback.print_exc()
			return None

