import datetime
from SmartAPI.model.Request import Request
from SmartAPI.model.Activity import Activity
from SmartAPI.smartapiexceptions.InsufficientDataException import InsufficientDataException
from SmartAPI.common.Tools import Tools
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.SystemOfInterest import SystemOfInterest
from SmartAPI.model.Evaluation import Evaluation

import traceback

class RequestFactory(object):
	
	def __init__(self):
		pass
	
	@classmethod
	def create(cls, generatedBy):
		request = Request()
		if (generatedBy is None or  generatedBy == ""):
			raise InsufficientDataException("Invalid smartapi:generatedBy URI.")

		g = Activity(generatedBy)
		g.clearTypes()
		request.setGeneratedBy(g)
		
		request.setGeneratedAt(datetime.datetime.now())

		return request;
	
	def fromString(self, data, serialization):
		try:
			return Request().parse(Tools().getResourceByType(RESOURCE.REQUEST, Tools().fromString(data, serialization)))
		except:
			print "Unable to parse Evaluation by type smartapi:Request from the given string."
			traceback.print_exc()
			return None

	def createRegistrationRequest(self, generatedBy):
		req = Request()
		if (generatedBy is None or (generatedBy is not None and generatedBy == "")):
			raise InsufficientDataException("Invalid registrant (smartapi:generatedBy) URI.");
		
		req.setGeneratedBy(Activity(generatedBy))
		
		# timestamp of when this message is being generated (now)
		req.setGeneratedAt(datetime.datetime.now())

		req.addType(RESOURCE.REQUEST)
		
		return reqd
