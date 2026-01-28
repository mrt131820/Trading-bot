from SmartAPI.rdf.List import List

class NudeList(List):

    def __init__(self):
        List.__init__(self)
        
    def add_items(self, items):
        
        if isinstance(items, list):
            for i in items:               
                try:  # objects support toNude, simple variables don't
                    self.elements.append(i.toNude())
                except:
                    self.elements.append(i)
        else:
            try:
                self.elements.append(items.toNude())
            except:
                self.elements.append(items)