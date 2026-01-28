import datetime
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools
from SmartAPI.model.Activity import Activity
from SmartAPI.model.Notification import Notification
from SmartAPI.smartapiexceptions.InsufficientDataException import InsufficientDataException

import traceback

class NotificationFactory(object):

	def __init__(self):
		pass
	
	def create(self, generatedBy):
		notification = Notification()
		if (generatedBy is None or (generatedBy is not None and generatedBy == "")):
			raise InsufficientDataException("Invalid seas:generatedBy URI.");

		g = Activity(generatedBy)
		g.clearTypes()
		notification.setGeneratedBy(g)

		# timestamp of when this message is being generated (now)
		notification.setGeneratedAt(datetime.datetime.now())
		
		return notification

	def fromString(self, data, serialization):
		try:
			return Notification().parse(Tools().getResourceByType(RESOURCE.NOTIFICATION, Tools().fromString(data, serialization)))
		except:
			print "Unable to parse Evaluation by type seas:Notification from the given string."
			traceback.print_exc()
			return None

