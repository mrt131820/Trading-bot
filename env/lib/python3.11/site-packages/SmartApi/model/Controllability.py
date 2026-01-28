from SmartAPI.model.Ability import Ability
from SmartAPI.common.RESOURCE import RESOURCE

class Controllability(Ability):

	def __init__(self, uri = None):
		Ability.__init__(self, uri)
		self.setType(RESOURCE.CONTROLLABILITY)

	
