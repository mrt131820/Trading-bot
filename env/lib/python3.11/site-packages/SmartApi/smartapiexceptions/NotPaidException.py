

class NotPaidException(Exception):
   
    def __init__(self, obj):
        self.unpaidObject = obj
    def getUnpaidObject(self):
        return self.unpaidObject
    