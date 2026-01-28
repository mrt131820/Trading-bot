from SmartAPI.common.HttpClient import HttpClient
import urllib2, json
import traceback
import os

class NS(object):	
    customOntologyPrefix = "http://smart-api.io/ontology/1.0/"
    triplestoreManagerAPIUri = 'http://talk.smart-api.io/develop/triplestoremanager' 
    customOntologydownloadUriPrefix = "http://seas.asema.com/develop/"
    
    
    jsonRequestID = 1
    httpClient = HttpClient()
    checksum = ''
    # prefix and URI pairs
    prefixes = {}
    
    # namespaces
    GEO = "http://www.w3.org/2003/01/geo/wgs84_pos#"
    OWL = "http://www.w3.org/2002/07/owl#"
    QUANTITY = "http://data.nasa.gov/qudt/owl/quantity#"
    QUDT = "http://data.nasa.gov/qudt/owl/qudt#"
    RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    RDFS = "http://www.w3.org/2000/01/rdf-schema#"
    SMARTAPI = "http://smart-api.io/ontology/1.0/smartapi#"
    UNIT = "http://data.nasa.gov/qudt/owl/unit#"
    VCARD = "http://www.w3.org/2006/vcard/ns#"
    XSD = "http://www.w3.org/2001/XMLSchema#"
    DC = "http://purl.org/dc/terms/"
    DRAFT = "http://smart-api.io/ontology/1.0/draft#"
    GR = "http://purl.org/goodrelations/v1#"
    
    @classmethod
    def toAbsoluteUri(cls, uri):
        '''
        If the uri uses a valid prefix, then this function can translate the prefix to URI string.
        This is the main API
        '''
        from SmartAPI.common.Tools import Tools
        
        try:
            #  if already absolute uri, return it
            if '://' in uri:
                return uri
            # if uri is prefixed 
            if ':' in uri:
                parts = uri.split(':')                
                prefixUri = cls.prefixToUri(parts[0])                
                # if prefix not recognized, try to update prefixes from ontology server
                if prefixUri is None:
                    cls.updatePrefixMap()                    
                    prefixUri = cls.prefixToUri(parts[0])                    
                # if prefix still not recognized
                if prefixUri is None:
                    print 'Prefix: ', parts[0], ' not recognized. Will continue assuming it is a custom Smart API ontology.'
                    # assume this is a custom smart api ontology prefix and use standard replace method and add to prefix mappings
                    cls.prefixes[parts[0].lower] = cls.customOntologyPrefix + parts[0] + "#"
                    prefixUri = cls.prefixToUri(parts[0])
                # prefix replaced successfully
                return prefixUri + parts[1]
            else:
                # uri is not absolute but also not prefix, nothing can do 
                return uri                                    
        except:
            print 'illegal URI found: ', uri
            traceback.print_exc()
            return uri

    @classmethod
    def prefixToUri(cls, prefix):
        '''
        Return uri string that the given prefix represents. If not found, return None.
        '''    	    	
        prefix = prefix.lower()
        if prefix in cls.prefixes:
            return cls.prefixes[prefix]  
        return None          
    
    @classmethod
    def updatePrefixMap(cls):
    	'''
    	generate or update NS.prefix.      	
    	'''
        if cls.checksum is not None and cls.checksum:
        	# local checksum exists, then try to fetch latest checksum from WebFront.
        	new_checksum = cls.fetchChecksumFromServer()
        	if new_checksum is None:
        		# if fetching checksum fails, chances are URI map fetching will also fail. So just try to fetch from local file.
        		cls.prefixes = cls.generatePrefixMapFromLocalFile()
        	else:
        		if new_checksum == cls.checksum:
        			print 'checksum and URI-prefix map are already up-to-date.'
        		else:
        			cls.prefixes = cls.fetchPrefixMapFromOntologyServer()        	
        else:
        	print 'local checksum is empty. Trying to fetch checksum and uri maps from WebFront server.'
        	cls.prefixes = cls.fetchPrefixMapFromOntologyServer()
                
       
    @classmethod
    def fetchChecksumFromServer(cls):
        '''
        send JSON request to get checksum from WebFront server
        @return checksum as string
        '''
        o = {}
        o['jsonrpc'] = '2.0'
        o['id'] = cls.jsonRequestID
        cls.jsonRequestID += 1
        o['method'] = 'sparql_query'
        
        param = {}
        param['ontology_filter'] = 'one'
        param['query_type'] = 'list_all_resources'
        o['params'] = param
        
        payload = json.dumps(o)        
        try:
            resp = cls.httpClient.sendPost(cls.triplestoreManagerAPIUri, payload, 'application/json', 'application/json')[0]
            o_resp = json.loads(resp)            
            checksum = o_resp['result']['checksum']
            return checksum
        except:
            print 'Unable to check updates for prefixes from the ontology server.'
            traceback.print_exc()
         
    @classmethod
    def fetchPrefixMapFromOntologyServer(cls):    
        '''
        send JSON request to get URIs and checksum from WebFront server, and save them locally.
        If the retrieving from WebFront server fails, then get URI and checksum from local file.
        @return: a URL-prefix map
        '''
        from SmartAPI.common.ConceptDetails import ConceptDetails
        
        url_map = {}
        
        o = {}
        o['jsonrpc'] = '2.0'
        o['id'] = cls.jsonRequestID
        cls.jsonRequestID += 1
        o['method'] = 'get_namespaces'
        o['params'] = {}
        
        payload = json.dumps(o)
        try:
            resp = cls.httpClient.sendPost(cls.triplestoreManagerAPIUri, payload, 'application/json', 'application/json')[0]
            o_resp = json.loads(resp)
            results = o_resp['result'] # results is a dictionary structure           
            for entry in results.values():                
                prefix = entry['prefix']
                uri = entry['namespace']
                path = entry['path']
                isCustom = entry['isCustom']                             
                # add to prefix map
                url_map[prefix] = uri
                # also add its downloadable ontology uri if it is custom url
                if isCustom:                     
                    if not uri in ConceptDetails.customUrlMap:                                                               
                        ConceptDetails.customUrlMap[uri] = cls.customOntologydownloadUriPrefix + path            
                        
            # if managed to fetch prefixes from ontology server
            if len(url_map)>0:
                # update checksum variable
                cls.checksum = cls.fetchChecksumFromServer()
                # write fetched prefixes and checksum to local file 
                if cls.checksum is not None:
                    cls.savePrefixMapToLocalFile(url_map, cls.checksum)
                    print 'Successfully fetched prefixes from the ontology server and stored on local file.'
                    return url_map
            else:
                print 'Unable to update prefixes from the ontology server. Use prefixes from local file.'            
                return cls.generatePrefixMapFromLocalFile()                
            
        except:
            print 'Unable to update prefixes from the ontology server. Use prefixes from local file.'
            #traceback.print_exc()
            return cls.generatePrefixMapFromLocalFile()
    
    @classmethod
    def generatePrefixMapFromLocalFile(cls):
    	'''
    	The URL maps and checksum on local file is from previous successful access to WebFront server. 
    	If such local file does not exist, then use hard-coded URL map, and in that case checksum will be cleared.
    	'''
    	url_map = {}
    	
    	cwd = os.getcwd()
    	filename = os.path.join(cwd, "prefix_local.txt")
    	
    	try:
	    	with open(filename) as handle:
	    		data = handle.read()
	    		o = json.loads(data)
	    		url_map = o['urls']
	    		cls.checksum = o['checksum']
        except:
            print 'Unable to read prefixes from from local file. Use hard-coded prefix map instead.'
            return cls.generatePrefixMapFromNSFields()
    	
    	if len(url_map)>0:
    		print 'Successfully loaded prefixes from local file.'
    	else:
    		print 'Prefixes from local file is empty. Use hard-coded prefix map instead.'
    		return cls.generatePrefixMapFromNSFields()
    	
    	return url_map
    
    @classmethod
    def savePrefixMapToLocalFile(cls, url_map, checksum):  
    	'''
    	store prefix-url map and checksum to a file located at the directory that the script is in. writing in JSON format  
    	'''
    	cwd = os.getcwd()
    	filename = os.path.join(cwd, "prefix_local.txt")
    	
    	with open(filename, 'w') as handle:
    		o = {}
    		o['urls'] = url_map
    		o['checksum'] = checksum
    		o_str = json.dumps(o)
    		handle.write(o_str)
		
    @classmethod
    def generatePrefixMapFromNSFields(cls):	
    	'''
    	copy hard-coded prefix-uri map provided in NS class.
    	'''    	
    	url_map = {}
    	
    	url_map['geo'] = NS.GEO
    	url_map['owl'] = NS.OWL
    	url_map['quantity'] = NS.QUANTITY
    	url_map['qudt'] = NS.QUDT
    	url_map['rdf'] = NS.RDF
    	url_map['rdfs'] = NS.RDFS
    	url_map['smartapi'] = NS.SMARTAPI
    	url_map['unit'] = NS.UNIT
    	url_map['vcard'] = NS.VCARD
    	url_map['xsd'] = NS.XSD
    	url_map['dc'] = NS.DC
    	url_map['draft'] = NS.DRAFT
    	url_map['gr'] = NS.GR
    	
    	cls.checksum = ''
    	
    	return url_map
    