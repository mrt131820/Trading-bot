from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.rdf.Resource import Resource

from SmartAPI.model.Entity import Entity

import traceback


class Organization(Entity):

	def __init__(self, uri = None):
		Entity.__init__(self, uri)
		self.setType(RESOURCE.ORGANIZATION)

