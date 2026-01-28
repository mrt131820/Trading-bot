from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.PriceSpecification import PriceSpecification

class UnitPriceSpecification(PriceSpecification):
    '''
    classdocs
    '''

    def __init__(self, uri = None):
        '''
        Constructor
        '''
        super(UnitPriceSpecification, self).__init__(uri)
        self.setType(RESOURCE.UNITPRICESPECIFICATION)
        