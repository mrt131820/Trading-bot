"""
A wrapper class around Python RDFLib methods to make a graph behave in a similar
way as Java Apache Jena model.
"""
import sys

try:
    from rdflib import Graph
    from rdflib import BNode
    from rdflib import URIRef
    from rdflib import Literal
    from rdflib.namespace import XSD, RDF
except:
    print "RDFLib is missing from your Python installation"
    print "Install it with"
    print ">  pip install rdflib"
    print ">  pip install rdflib-jsonld"
    sys.exit()

from SmartAPI.common.SERIALIZATION import SERIALIZATION
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.NS import NS
from SmartAPI.rdf.LinkedList import LinkedList
from SmartAPI.rdf.OrderedList import OrderedList
from SmartAPI.rdf.ItemizedList import ItemizedList
from SmartAPI.rdf.NudeList import NudeList
from SmartAPI.rdf.RdfLiteral import RdfLiteral
from SmartAPI.rdf.Property import Property
from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.Statement import Statement

import simplejson
import traceback


class Model(object):

    def __init__(self):
        self.graph = Graph()
        self.top_nodes = []
        self.serializedResources = []
        
    def createResource(self, id = None):
        return Resource(id = id, model = self)
    
    def createProperty(self, id = None):
        return Property(id)

    def createLiteral(self, element):
        return Literal(element)
    
    def createTypedLiteral(self, element, type):
        return self._convert_element(element, type)
    
    def createOrderedList(self):
        return OrderedList()
    
    def createItemizedList(self):
        return ItemizedList()
    
    def createLinkedList(self):
        return LinkedList()
    
    def createNudeList(self):
        return NudeList()
    
    def _append_to_graph(self, subject, predicate, object):
       
        if isinstance(predicate, Property):
            self.graph.add((subject, URIRef(predicate.id), object))
        else:
            self.graph.add((subject, predicate, object))
    
    def _add_statement(self, statement):
        if statement is not None:
            #print "Adding statement", statement
            self._append_to_graph(statement.getSubject(), statement.getPredicate(), statement.getObject())
        
    # Append various types of elements to the graph. This is the main method for determining
    # the type of a serializable object and creating the appropriate triple for it. All methods
    # that need to make additions to the graph should use it, unless handling raw triples
    # the the form of s-p-o of a statement that embeds them
    def _add_element(self, object, predicate, subject = None):
        from SmartAPI.rdf.Variant import Variant
        from SmartAPI.common.Tools import Tools
        
        if isinstance(object, Resource) and (object not in self.serializedResources):
            self.serializedResources.append(object)  
                    
            n = object.getNode()
            
            for p in object.listProperties():
                if p is not None:
                    if isinstance(p, list):
                        for pe in p:
                            self._add_statement(pe)
                            if pe.getResource() is not None:
                                self._add_element(pe.getResource(), pe.getPredicate(), n)
                    else:
                        self._add_statement(p)
                        if p.getResource() is not None:
                            self._add_element(p.getResource(), p.getPredicate(), n)
            
            for l in object.listLiterals():
                self._add_statement(l)
        
        elif isinstance(object, Resource) and (object in self.serializedResources): 
            pass
        
        elif isinstance(object, Property):
            if subject is not None and predicate is not None and object.id is not None:
                self._append_to_graph(subject, predicate, URIRef(object.id))
        
        elif isinstance(object, Literal):
            if subject is not None and predicate is not None:
                self._append_to_graph(subject, predicate, object)
                
        elif isinstance(object, RdfLiteral):
            if subject is not None and predicate is not None:
                self._append_to_graph(subject, predicate, object.getValue())
        
        elif isinstance(object, Variant):
            if subject is not None and predicate is not None:
                self._append_to_graph(subject, predicate, object.asTerm())
        
        elif isinstance(object, URIRef):
            self._append_to_graph(subject, predicate, object)
            
        else:
            self._append_to_graph(subject, predicate, Literal(object))
    
        """
        elif isinstance(object, list):  # ordered list is the default for raw lists
            self._add_ordered_list(object, predicate, subject)

        elif isinstance(object, OrderedList):
            self._add_ordered_list(object, predicate, subject)
        
        elif isinstance(object, LinkedList):
            self._add_linked_list(object, predicate, subject)
            
        elif isinstance(object, ItemizedList):
            self._add_itemized_list(object, predicate, subject)
        """
    def _convert_element(self, element, type):
        return Literal(element, datatype = URIRef(type))
    
    def is_list(self, node):
        item = self.graph.value(subject=node, predicate=RDF.first)
        return item is not None
        
    def parse_list(self, container, parent_node = None, klass = None, first = None):
      
        if first is None and parent_node is not None:
            first = self.graph.value(subject=parent_node, predicate=RDF.first)
        if first is not None:
            arr = self.graph.value(subject=parent_node, predicate=RDF.rest)
            if arr:
                return self._parse_linked_list(container, first, arr, klass)
            
            arr = self.graph.value(subject=first, predicate=URIRef(NS.SMARTAPI + "rawArray"))
            if arr:
                return self._parse_nude_list(container, first, klass)
            
            arr = self.graph.value(subject=first, predicate=URIRef(NS.SMARTAPI + "array"))
            if arr:
                return self._parse_itemized_list(container, first, klass)
            
            arr = self.graph.value(subject=first, predicate=URIRef(NS.SMARTAPI + "indexedArray"))
            if arr:
                return self._parse_ordered_list(container, first, klass)
            
        return None
    
    def _parse_list_entry(self, entry, klass = None, from_nude = False):
        from SmartAPI.model.ValueObject import ValueObject
        from SmartAPI.rdf.Variant import Variant
        from SmartAPI.common.Tools import Tools
       
        if from_nude and klass is not None:
            item = klass()
            item.fromNude(entry)
            return item
        
        if isinstance(entry, Literal):
            return Variant(entry.toPython())
        elif isinstance(entry, URIRef):
            if entry == RDF.nil:
                return None
            return Variant(entry)
        else:
            if klass is None:
                types = []
                sl = self.listStatements(subject = entry, predicate = URIRef(PROPERTY.RDF_TYPE), object = None)
                for s in sl:
                    types.append(s.getResource().toString())
                klass = Tools().mapper.getClass(types, default = Variant)
  
            item = klass()
            for s in self.find_statements_for_node(entry):
                if s.predicate == NS.SMARTAPI + "valueObject":
                    itemv = ValueObject()
                    for sv in self.find_statements_for_node(s.object):
                        itemv.parse(sv)
                    item.addValueObject(itemv)
                else:
                    item.parseStatement(s)
            return item
    
    def _parse_linked_list(self, container, value, next, klass):
        if value is not None:
            item = self._parse_list_entry(value, klass)
            if item: container.append(item)
        
        if next is not None:
            value = self.graph.value(subject=next, predicate=RDF.first)
            next = self.graph.value(subject=next, predicate=RDF.rest)
            self._parse_linked_list(container, value, next, klass)
            
        return 'LinkedList'
    
    def _parse_nude_list(self, container, current, klass):
        arr = self.graph.value(subject=current, predicate=URIRef(NS.SMARTAPI + "rawArray"))
        if arr:
            value = self.graph.value(subject=arr, predicate=RDF.value)
            v = simplejson.loads(value.toPython())
            for o in v:
                container.append(self._parse_list_entry(o, klass, from_nude = True))
        
        return 'NudeList'
    
    def _parse_itemized_list(self, container, current, klass):
                
        arr = self.graph.value(subject=current, predicate=URIRef(NS.SMARTAPI + "array"))
        size = self.graph.value(subject=current, predicate=URIRef(NS.SMARTAPI + "size"))
        if arr:
            for s, p, o in self.graph.triples( (arr, RDF.value, None) ):
                container.append(self._parse_list_entry(o, klass))
        
        return 'ItemizedList'
    
    def _parse_ordered_list(self, container, current, klass):
        arr = self.graph.value(subject=current, predicate=URIRef(NS.SMARTAPI + "indexedArray"))
        size = self.graph.value(subject=current, predicate=URIRef(NS.SMARTAPI + "size"))
        if arr and size:
            # prefill
            for i in range(size.toPython()):
                container.append(None)
            #container = [None] * size.toPython()
            for s, p, o in self.graph.triples( (arr, URIRef(NS.SMARTAPI + "entry"), None) ):
                index = self.graph.value(subject=o, predicate=URIRef(NS.SMARTAPI + "index"))
                value = self.graph.value(subject=o, predicate=RDF.value)
                container[index.toPython()] = self._parse_list_entry(value, klass)
        
        return 'OrderedList'
    # obsolete?
    """
    def _add_linked_list(self, rdflist, predicate, subject):
        from SmartAPI.model.Obj import Obj
        from SmartAPI.rdf.Variant import Variant

        elements = rdflist.get_items()
        current = lst = BNode()
        self.graph.add((subject, URIRef(predicate.id), lst))
        l = len(elements)
        for index, var in enumerate(elements):
            if isinstance(var, Variant):  # support lists with raw values (not just wrapped inside Evaluation
                self.graph.add((current, RDF.first, var.asTerm()))
            elif isinstance(var, Obj):
                self._add_element(var.serialize(self), RDF.first, subject = current)
            elif isinstance(var, Resource):
                var_node = BNode()
                for p in var.properties:
                    self._add_element(p[1], URIRef(p[0]), subject = var_node)
                self.graph.add((current, RDF.first, var_node))
            else:
                self.graph.add((current, RDF.first, Literal(var)))
            
            next = RDF.nil if index == l-1 else BNode()  # last item
            self.graph.add((current, RDF.rest, next))
            current = next
    """
    
    def add(self, statement):
        if isinstance(statement, list):
            for l in statement:
                self._add_element(l, None)
        else:
            self._add_element(statement, None)

    def findSubject(self, predicate, object):
        return Resource(model = self, node = self.graph.value(predicate = predicate, object=object))
    
    def findObject(self, subject, predicate):
        return Statement(node = self.graph.value(subject = subject, predicate = predicate), subject = subject, predicate = predicate)
    
    def find_statements_for_node(self, node, predicate = None):
        r = []
        
        for s, p, o in self.graph.triples( (node, predicate, None) ):
            r.append(Statement(model = self, subject = s, predicate = p, object = o, resource = Resource(model = self, node = o)))
        return r
    
    def listStatements(self, subject = None, predicate = None, object = None):
        r = []
        for s, p, o in self.graph.triples( (subject, predicate, object) ):
            r.append(Statement(model = self, subject = s, predicate = p, object = o, resource = Resource(model = self, node = o)))
        return r
    
    def serialize(self, format = SERIALIZATION.JSON_LD):
        return self.graph.serialize(format=format)
    
    def parse(self, data = None, file = None, format = SERIALIZATION.JSON_LD):
        if data is not None:
            try:
                if format == SERIALIZATION.JSON_LD:
                    json = simplejson.loads(data)
                    if isinstance(json, dict) and json.has_key('@graph') and json.has_key('@context'):
                        self.graph.parse(data = simplejson.dumps(json['@graph']), format='json-ld', context=json['@context'])
                    else:
                        self.graph.parse(data = data, format='json-ld')
                # other formats
                else:
                    self.graph.parse(data = data, format=format)
            except:
                print "Could not read the input data into a graph"
                #traceback.print_exc()
                traceback.print_stack()
            return
        
        elif file is not None:
            try:
                f = open(file)
                self.graph.parse(f, format=format)
                f.close()
            except:
                print "Could not read the file into a model"
                traceback.print_exc()
            return
        print "No input to parse into a graph"
