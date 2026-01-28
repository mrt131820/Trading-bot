from SmartAPI.model.Entity import Entity

class AbstractEntity(Entity):

	def __init__(self, uri = None):
		Entity.__init__(self, uri)
	
	
