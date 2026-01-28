class NotFoundException(Exception):

	def __init__(self, message):
		super(NotFoundException, self).__init__(message)
