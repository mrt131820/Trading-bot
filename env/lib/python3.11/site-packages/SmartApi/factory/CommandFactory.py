import datetime 
from SmartAPI.model.Evaluation import Evaluation
from SmartAPI.model.Activity import Activity
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools
from SmartAPI.smartapiexceptions.InsufficientDataException import InsufficientDataException
import traceback

class CommandFactory(object):

	def __init__(self):
		pass
	
	def create(self, generatedBy):
		evaluation = Evaluation()
		if (generatedBy is None or (generatedBy is not None and generatedBy == "")):
			raise InsufficientDataException("Invalid command generator id (seas:generatedBy) URI.")

		g = Activity(generatedBy)
		g.clearTypes()
		evaluation.setGeneratedBy(g)
		
		# timestamp of when this message is being generated (now)
		evaluation.setGeneratedAt(datetime.datetime.now())

		evaluation.addType(RESOURCE.COMMAND)
		
		return evaluation;

	
	def fromString(self, data, serialization):
		try:
			return Evaluation().parse(Tools().getResourceByType(RESOURCE.COMMAND, Tools().fromString(data, serialization)))
		except:
			print "Unable to parse Evaluation by type seas:Command from the given string."
			traceback.print_exc()
			return None
		