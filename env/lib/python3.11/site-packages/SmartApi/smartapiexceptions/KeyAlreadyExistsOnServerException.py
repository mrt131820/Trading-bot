class KeyAlreadyExistsOnServerException(Exception):
    def __init__(self):
        super(KeyAlreadyExistsOnServerException, self).__init__()
        