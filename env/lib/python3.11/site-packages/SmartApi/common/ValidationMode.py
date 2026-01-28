
class ValidationMode(object):
    # no validation, everything is allowed
    NO_VALIDATION = 0
    # validation is done using current online ontology resources (custom ontologies are from WebFront server)
    REALTIME_VALIDATION = 1
    # validation is done against the locally cached files
    LOCAL_VALIDATION = 2


    