class NotAuthorizedException(Exception):
   
    def __init__(self):
        super(NotAuthorizedException, self).__init__()