class InsufficientDataException(Exception):

	def __init__(self, message):
		super(InsufficientDataException, self).__init__(message)

