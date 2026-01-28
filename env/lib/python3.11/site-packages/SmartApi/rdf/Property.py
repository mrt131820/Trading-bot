"""
A wrapper class around Python RDFLib methods to make a graph behave in a similar
way as Java Apache Jena model.
"""

class Property(object):
    def __init__(self, id):
        self.id = id
        
    def getUri(self):
        return self.id