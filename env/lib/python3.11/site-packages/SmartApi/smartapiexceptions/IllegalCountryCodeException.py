
class IllegalCountryCodeException(Exception):

	def __init__(self, message):
		super(IllegalCountryCodeException, self).__init__(message)

