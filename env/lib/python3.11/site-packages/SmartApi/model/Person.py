from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.rdf.Resource import Resource

from SmartAPI.model.PhysicalEntity import PhysicalEntity

import traceback

class Person(PhysicalEntity):

	def __init__(self, uri = None):
		PhysicalEntity.__init__(self, uri)
		self.setType(RESOURCE.PERSON)
