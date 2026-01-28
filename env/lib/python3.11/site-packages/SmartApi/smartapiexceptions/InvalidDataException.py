class InvalidDataException(Exception):

	def __init__(self, message):
		super(InvalidDataException, self).__init__(message)

		