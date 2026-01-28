
class RevokeException(Exception):
   
    def __init__(self, message):
        super(RevokeException, self).__init__(message)
