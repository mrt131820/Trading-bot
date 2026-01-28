from SERIALIZATION import SERIALIZATION

class CONTENTTYPE(object):
	TURTLE		= "text/turtle"
	TURTLE_ALT	= "application/x-turtle"
	JSON_LD		= "application/ld+json"
	RDF_XML		= "application/rdf+xml"
	N_TRIPLE	= "application/n-triples"
	RDF_JSON	= "application/rdf+json"
	RDF_XML_ABBREV = "application/rdf+xml"
	UNKNOWN		= "Unknown"

	mapping = {
		TURTLE: SERIALIZATION.TURTLE,
		TURTLE_ALT: SERIALIZATION.TURTLE,
		JSON_LD: SERIALIZATION.JSON_LD,
		RDF_XML: SERIALIZATION.RDF_XML,
		N_TRIPLE: SERIALIZATION.N_TRIPLE,
		RDF_JSON: SERIALIZATION.RDF_JSON,
		RDF_XML_ABBREV: SERIALIZATION.RDF_XML_ABBREV,
		UNKNOWN: SERIALIZATION.TURTLE
	}

