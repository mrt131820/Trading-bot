"""
A wrapper class around Python RDFLib methods to make a graph behave in a similar
way as Java Apache Jena model.
"""
import sys
import traceback

try:
    from rdflib import BNode, URIRef, Literal
except:
    import sys
    print "RDFLib is missing from your Python installation"
    print "Install it with"
    print ">  pip install rdflib"
    print ">  pip install rdflib-jsonld"
    sys.exit()

from SmartAPI.rdf.LinkedList import LinkedList
from SmartAPI.rdf.OrderedList import OrderedList
from SmartAPI.rdf.ItemizedList import ItemizedList
from SmartAPI.rdf.NudeList import NudeList
from SmartAPI.rdf.RdfLiteral import RdfLiteral
from SmartAPI.common.NS import NS
from rdflib.namespace import RDF


class Resource(object):
    def __init__(self, id = None, model = None, node = None):
        # if node is not None: print dir(node)
        self.properties = {}
        self.literals = {}
        self.id = id
        self.model = model
        self.node = node
        if node is not None and id is None and isinstance(node, URIRef):
            self.id = str(node)
        if self.node is None:
            if id is None:
                self.node = BNode()
            else:
                self.node = URIRef(id)
    
    def toString(self):
        return str(self.node)
    
    def isAnon(self):
        return isinstance(self.node, BNode)
    
    def addProperty(self, propertyType, property):
        if self.properties.has_key(propertyType.getUri()):
            self.properties[propertyType.getUri()].append(property)
        else:            
            self.properties[propertyType.getUri()] = [property]
            
    def addLiteral(self, literalType, literal):
        if self.literals.has_key(literalType.getUri()):
            self.literals[literalType.getUri()].append(literal)
        else:
            self.literals[literalType.getUri()] = [literal]

    def getId(self):
        return self.id
    
    def getProperties(self):
        return self.properties
    
    def getProperty(self, property = None):
        if property is None:
            return self.properties
        else:
            if self.properties.has_key(property.getUri()):
                l = self.properties[property.getUri()]
                if len(l) > 0:
                    return self.createStatement(self.model, property.getUri(), l[0])
            return None

    def getLiterals(self):
        return self.literals

    def getNode(self):
        return self.node
    
    def getModel(self):
        return self.model
    
    def createStatement(self, m, predicateUri, obj, subject = None):
        from SmartAPI.rdf.Statement import Statement
        from SmartAPI.rdf.Variant import Variant
        
        s = Statement(m)
        s.setSubject(subject)
        s.setPredicate(URIRef(predicateUri))
        object = None
        
        if isinstance(obj, Literal):
            object = obj
        elif isinstance(obj, URIRef):
            object = obj
        elif isinstance(obj, Variant):
            object = obj.asTerm()
        elif isinstance(obj, RdfLiteral):
            object = self.makeLiteral(obj)
        elif isinstance(obj, Resource):
            object = obj.getNode()
            s.setResource(obj)
        else:
            object = self.makeLiteral(obj)
        
        s.setObject(object)
    
        return s

    def createOrderedListStatements(self, model, predicateUri, obj):
        from SmartAPI.rdf.Statement import Statement
        from SmartAPI.model.Obj import Obj
        from SmartAPI.rdf.Variant import Variant
        
        if isinstance(obj, list):
            lst = obj
        else:
            lst = obj.get_items()
        l = len(lst)
        
        ss = []
        bNode = BNode()
        arr = BNode()
               
        # Initial blank node
        ss.append(Statement(model = model, subject = self.node, predicate = URIRef(predicateUri), object = bNode))
        # Size
        ss.append(Statement(model = model, subject = bNode, predicate = URIRef(NS.SMARTAPI + "size"), object = Literal(l)))
        # The array that holds entries
        ss.append(Statement(model = model, subject = bNode, predicate = URIRef(NS.SMARTAPI + "indexedArray"), object = arr))
        
        for index in range(l):
            var = lst[index]
            o, o_stmt = self._var_to_statements(var)
            if o_stmt is not None: ss.extend(o_stmt)

            entry = BNode()
            ss.append(Statement(model = model, subject = arr, predicate = URIRef(NS.SMARTAPI + "entry"), object = entry))
            ss.append(Statement(model = model, subject = entry, predicate = URIRef(NS.SMARTAPI + "index"), object = Literal(index)))
            ss.append(Statement(model = model, subject = entry, predicate = URIRef(RDF.value), object = o))
        
        return ss
    
    def createItemizedListStatements(self, model, predicateUri, obj):
        from SmartAPI.rdf.Statement import Statement
        from SmartAPI.model.Obj import Obj
        from SmartAPI.rdf.Variant import Variant
        
        lst = obj.get_items()
        l = len(lst)
        
        ss = []
        bNode = BNode()
        arr = BNode()
        
        # Initial blank node
        ss.append(Statement(model = model, subject = self.node, predicate = URIRef(predicateUri), object = bNode))

        # Size
        ss.append(Statement(model = model, subject = bNode, predicate = URIRef(NS.SMARTAPI + "size"), object = Literal(l)))
        
        # The array that holds entries
        ss.append(Statement(model = model, subject = bNode, predicate = URIRef(NS.SMARTAPI + "array"), object = arr))
        
        for index in range(l):
            var = lst[index]
            o, o_stmt = self._var_to_statements(var)
            if o_stmt is not None: ss.extend(o_stmt)
            ss.append(Statement(model = model, subject = arr, predicate = URIRef(RDF.value), object = o))
        
        return ss
    
    def createLinkedListStatements(self, model, predicateUri, obj):
        from SmartAPI.rdf.Statement import Statement
        lst = obj.get_items()
        ss = []        
        
        #bNode = current = self.node
        bNode = BNode()
        current = bNode
               
        # Initial blank node
        ss.append(Statement(model = model, subject = self.node, predicate = URIRef(predicateUri), object = bNode))
        
        l = len(lst)
        for index in range(l):
            var = lst[index]
            o, o_stmt = self._var_to_statements(var)
            if o_stmt is not None: ss.extend(o_stmt)
            
            # Statement for the rest of the list
            if index == l-1: # last item, put in nil
                next = RDF.nil
            else:
                next = BNode() # not last, need a new blank node
        
            ss.append(Statement(model = model, subject = current, predicate = RDF.first, object = o))
            ss.append(Statement(model = model, subject = current, predicate = RDF.rest, object = next))
            current = next # set pointer ready for the next loop
        
        return ss
    
    def createNudeListStatements(self, model, predicateUri, obj):
        from SmartAPI.rdf.Statement import Statement
        import simplejson
        
        lst = obj.get_items()
        l = len(lst)
        ss = []
        
        bNode = BNode()
        arr = BNode()
        
        # Initial blank node
        ss.append(Statement(model = model, subject = self.node, predicate = URIRef(predicateUri), object = bNode))

#         # Size
#         ss.append(Statement(model = model, subject = bNode, predicate = URIRef(NS.SMARTAPI + "size"), object = Literal(l)))
        
        # The array that holds entries
        ss.append(Statement(model = model, subject = bNode, predicate = URIRef(NS.SMARTAPI + "rawArray"), object = arr))
               
        ss.append(Statement(model = model, subject = arr, predicate = RDF.value, object = Literal(simplejson.dumps(lst))))
        
        return ss
    
    def _var_to_statements(self, var):
        from SmartAPI.model.Obj import Obj
        from SmartAPI.rdf.Variant import Variant
        
        ostmt = None
        # Statement for first list element (the actual object)
        if isinstance(var, RdfLiteral):
            o = self.makeLiteral(var)
        elif isinstance(var, Resource):
            o = BNode()
            ostmt = var.listProperties(subject = o)
        elif isinstance(var, Variant):
            o = var.asTerm()
        elif isinstance(var, Obj):
            r = var.serialize(self.model)
            o = r.getNode()
            ostmt = r.listProperties()
        else:
            o = Literal(var)
        
        return o, ostmt
    
    def listProperties(self, property = None, subject = None):
        statements = []

        if property:
            if self.properties.has_key(property.getUri()):
                statements.extend(self._fetch_properties(subject, property.getUri()))
        else:
            for propertyUri in self.properties:
                statements.extend(self._fetch_properties(subject, propertyUri))
 
        return statements
    
    def _fetch_properties(self, subject, uri):
        statements = []
        if subject is None: subject = self.node
        
        l = self.properties[uri]
        for property in l:
            # Convert various types of lists into statements. For raw Python lists OrderedList is the defaults
            if isinstance(property, OrderedList) or isinstance(property, list):
                statements.append(self.createOrderedListStatements(self.model, uri, property))
                
            elif isinstance(property, ItemizedList):
                statements.append(self.createItemizedListStatements(self.model, uri, property))
        
            elif isinstance(property, LinkedList):
                statements.append(self.createLinkedListStatements(self.model, uri, property))
            
            elif isinstance(property, NudeList):
                statements.append(self.createNudeListStatements(self.model, uri, property))
            
            else: # Convert other types of properties into statements
                s = self.createStatement(self.model, uri, property, subject)
                if s is not None: 
                    statements.append(s)

        return statements

    def listLiterals(self):
        statements = []

        for propertyUri in self.literals:
            l = self.literals[propertyUri]
            for property in l:
                s = self.createStatement(self.model, propertyUri, property)
                if s is not None: 
                    statements.append(s)

        return statements
    
    def findProperties(self):
        return self.model.find_statements_for_node(self.node)
    
    def findProperty(self, p):
        return self.model.find_statements_for_node(self.node, predicate = URIRef(p.getUri()))

    # transforms the resource into a Python list. Requires that the node
    # is in the form of an RDF list (has first, rest properties
    def toList(self, klass):   
        '''
        @return: l - a python list
        @return: listType - a string to bookkeeping what type of Seas List
        '''    
        l = []
        sl = self.model.listStatements(subject = self.node, predicate = URIRef(RDF.first), object = None)
        for s in sl:
            listType = self.model.parse_list(l, parent_node = s.getSubject(), first = s.getObject(), klass = klass)
            break        
        return l, listType

    def makeLiteral(self, l):
        if isinstance(l, RdfLiteral):
            return Literal(l.getValue())
        else:
            return Literal(l)
   