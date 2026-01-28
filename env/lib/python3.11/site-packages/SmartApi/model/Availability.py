from SmartAPI.common.RESOURCE import RESOURCE

from SmartAPI.model.Ability import Ability
from SmartAPI.rdf.Resource import Resource

class Availability(Ability):

	def __init__(self, uri = None):
		Ability.__init__(self, uri)
		self.setType(RESOURCE.AVAILABILITY);
		
	
