
class SERIALIZATION(object):
	TURTLE = "turtle"
	JSON_LD = "json-ld"
	#RDF_XML = "pretty-xml"
	RDF_XML = "xml"
	N_TRIPLE = "nt"
	RDF_JSON = "rdf/json"
	RDF_XML_ABBREV = "rdf/xml-abbrev"
	
	
	@classmethod
	def getMimeType(cls, serialization):
		'''
		 @return Internet media type for some of aforementioned serialization format,
		 which is needed for wrapping rdf string into MIME message 
	 	Reference: Wikipedia and other online resources
		'''
		if serialization.lower() == cls.TURTLE:
			return 'text/turtle'
		elif serialization.lower() == cls.RDF_XML:
			return 'application/rdf+xml'
		elif serialization.lower() == cls.N_TRIPLE:
			return 'application/n-triples'
		elif serialization.lower() == cls.JSON_LD:
			return 'application/ld+json'	
	