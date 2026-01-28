from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.ServiceProvider import ServiceProvider


class WeatherServiceProvider(ServiceProvider):

	def __init__(self, uri = None):
		ServiceProvider.__init__(self)
		self.addType(RESOURCE.WEATHERSERVICEPROVIDER);
		self.setIdentifierUri(uri);
		


