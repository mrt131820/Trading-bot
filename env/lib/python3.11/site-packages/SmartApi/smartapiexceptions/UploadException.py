

class UploadException(Exception):
   
    def __init__(self, message):
        super(UploadException, self).__init__(message)
        
