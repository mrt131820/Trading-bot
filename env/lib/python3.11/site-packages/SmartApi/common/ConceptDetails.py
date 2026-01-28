from rdflib import Graph, URIRef, RDF
import rdflib
import urllib2
import traceback
from SmartAPI.common.NS import NS
import tempfile 

class ConceptDetails(object):
    '''
    used by Obj.explain() method. It fetches concept detail from seas Ontologies via URLs 
       
    '''
    # it stores ontologies in nsUrlMap. It can be huge, so these ontology are loaded one by one only when necessary. 
    ontStore = None 
    # for downloading ontologies from Internet. These urls are needed for explain() function
    nsUrlMap = {NS.SMARTAPI: 'http://seas.asema.com/smartapi-1.0.ttl',
                NS.QUDT: 'http://www.qudt.org/qudt/owl/1.0.0/qudt.owl',
                NS.QUANTITY: 'http://www.qudt.org/qudt/owl/1.0.0/quantity.owl',
                NS.UNIT: 'http://www.qudt.org/qudt/owl/1.0.0/unit.owl',
                NS.GR: 'http://purl.org/goodrelations/v1.owl',
                NS.GEO: 'http://www.w3.org/2003/01/geo/wgs84_pos#',
                NS.DC: 'http://dublincore.org/2012/06/14/dcterms.rdf',
                NS.VCARD: 'http://www.w3.org/2006/vcard/ns#'}
            
    loadedOnt = []    
    
    # The following variables are only needed for conceptvalidation
    # for downloading customer ontology. For  now assum all custom ontologies
    # are in Turtle
    customUrlMap = {} 
    # for downloading RDF, RDFS, OWL ontology. They are not needed for explain() function,
    # but needed for concept validatino (real-time)
    coreUrlMap = {NS.RDF: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  NS.RDFS: 'http://www.w3.org/2000/01/rdf-schema',
                  NS.OWL: 'http://www.w3.org/2002/07/owl#'}
    # it stores ontologies in customUrlMap and coreUrlMap
    coreCustomOntStore = None # it com
    
    
   
    # create temporary folder for keeping persistent graph store.
    tmpdir = tempfile.mkdtemp()        
                     
    @classmethod 
    def getComments(cls, resourceUri, NSstr):  
        '''
        @param resourceUri: URI string of the resource
        @param NSstr: Namespace as string
         
        @return rdfs:label and rdfs:comments value of this Resource as a String
        '''
        if (NSstr not in cls.loadedOnt) and cls.nsUrlMap.has_key(NSstr) :
            
            if NSstr in [NS.VCARD, NS.SMARTAPI]:               
                cls.loadAdditionalOntology(cls.nsUrlMap[NSstr], 'turtle')
            else:
                cls.loadAdditionalOntology(cls.nsUrlMap[NSstr], 'xml')
            cls.loadedOnt.append(NSstr)
        
        label = cls.ontStore.label(URIRef(resourceUri))
        comment = cls.ontStore.comment(URIRef(resourceUri))
                      
        return '%s  [%s]' % (label, comment) 
       
    @classmethod
    def loadAdditionalOntology(cls, sourceURL, formatStr):
        '''
        It load additional Ontology based on sourceURL, set self.ontStore with the extended ontology graph
        
        @param sourceURL: URL string where the ontology can be downloaded
        @param formatStr: string, e.g., 'xml' or 'turtle' 
       
        '''
        print '\n ***************** loading ontology from ', sourceURL,'************* \n'
        try:
            if cls.ontStore is None:
                firstOnt = Graph(store='Sleepycat', identifier='seasGraph')
                firstOnt.open(cls.tmpdir, create = True)        
                firstOnt.parse(sourceURL, format = formatStr)                      
                cls.ontStore = firstOnt                
            else:                           
                addOnt = Graph()
                addOnt.parse(sourceURL, format = formatStr)
                cls.ontStore = cls.ontStore + addOnt            
        except:
            print 'ERROR with downloading ontology.  should try again.' 
            traceback.print_exc()
    
    @classmethod
    def loadCoreCustomOntStore(cls):
        '''
        load all custom ontologies and core ontologies (RDF, RDFS, OWL) in one go.
        '''
        print '\n -------- loading custom and core ontologies from online resource.----- \n'
        try:
            cls.coreCustomOntStore = Graph()
            for ns, url in cls.coreUrlMap.iteritems():
                cls.coreCustomOntStore.parse(url)
            for ns2, url2 in cls.customUrlMap.iteritems():
                cls.coreCustomOntStore.parse(url2)
        except:
            traceback.print_exc()
    
    @classmethod
    def checkCoreCustomResource(cls, resourceUri):
        '''
        check whether a given resourceUri exist in custom or core ontology.
        @return boolean value
        '''
        r = URIRef(resourceUri)
        return (r, None, None) in cls.coreCustomOntStore  
    
    @classmethod 
    def checkOtherResource(cls, resourceUri, NSstr):  
        '''
        check whether a given resourceUri exist in ontology listed in nsUrlMap         
        @return boolean value
        '''
        if (NSstr not in cls.loadedOnt) and cls.nsUrlMap.has_key(NSstr) :
            
            if NSstr in [NS.VCARD, NS.SMARTAPI]:               
                cls.loadAdditionalOntology(cls.nsUrlMap[NSstr], 'turtle')
            else:
                cls.loadAdditionalOntology(cls.nsUrlMap[NSstr], 'xml')
            cls.loadedOnt.append(NSstr)
        
        r = URIRef(resourceUri)                      
        return (r, None, None) in cls.ontStore 
                
    @classmethod
    def close(cls):
        '''
        free opened resources/clean up
        '''
        import shutil
        
        print '\n\n CONCEPTDETAILS: clean up resources used by ConceptDetails.....'
        if cls.ontStore is not None:
            cls.ontStore.close()
        shutil.rmtree(cls.tmpdir)
        
        