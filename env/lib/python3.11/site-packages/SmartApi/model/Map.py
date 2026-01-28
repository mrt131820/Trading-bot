from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.Tools import Tools
from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.Variant import Variant

from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.Property import Property
from SmartAPI.rdf.types import *
from rdflib import Literal
from rdflib.namespace import RDF

from SmartAPI.common.Tools import Tools

import traceback

class Map(Obj):

	def __init__(self, identifier = None):
		Obj.__init__(self, identifier)
		self.setType(RESOURCE.MAP)
		self.map = {}
		
	def isEmpty(self):
		return len(self.map.keys()) == 0
	
	def size(self):
		return len(self.map.keys())
	
	def containsKey(self, key):
		return self.map.has_key(key)
	
	def containsValue(self, value):
		# FIXME
		return False

	def get(self, key):
		if self.map.has_key(key):
			return self.map[key]
		else:
			print "Error: the given key not found in Map"
			print "Available keys:", self.map.keys()
			return None

	def value(self, key):
		var = self.get(key)
		if var is not None:
			if isinstance(var, Variant):
				return var.getValue()
		return var
					
	def add(self, key, value):
		print "Error, a Map does not support the add method, use insert instead"
		
	def put(self, key, value):
		self.map[key] = value
		
	def insert(self, key, value):
		self.put(key, value)
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)
		
		resource = super(Map, self).serialize(model)
	
		keys = self.map.keys()
		for key in keys:
			entryResource = model.createResource()
			if isinstance(key, Obj):
				entryResource.addProperty(model.createProperty(PROPERTY.KEY), key.serialize(model))
			else:
				entryResource.addProperty(model.createProperty(PROPERTY.KEY), Literal(key))
			
			if isinstance(self.map[key], Obj) or isinstance(self.map[key], Variant):
				entryResource.addProperty(model.createProperty( PROPERTY.RDF_VALUE ), self.map[key].serialize(model))
			elif isinstance(self.map[key], list):
				rdfList = model.createOrderedList()
				rdfList.add_items(self.map[key])
				listContainer = model.createResource()
				listContainer.addProperty(Property(RDF.first), rdfList)
				entryResource.addProperty(model.createProperty(PROPERTY.RDF_VALUE), listContainer)
			else:
				entryResource.addProperty(model.createProperty(PROPERTY.RDF_VALUE), Literal(self.map[key]))
			
			resource.addProperty(model.createProperty(PROPERTY.ENTRY), entryResource)

		return resource


	def parseStatement(self, statement):
		from SmartAPI.rdf.Variant import Variant
		
		
		# get predicate
		predicate = str(statement.getPredicate())
		
		if predicate == PROPERTY.KEY or predicate == PROPERTY.RDF_VALUE:
			return # Don't handle the key and value separately, they are parsed as the children of an entry
			
		# entry
		if predicate == PROPERTY.ENTRY:
			entry = statement.getResource()
			keyStmt = entry.findProperty(entry.getModel().createProperty(PROPERTY.KEY))
			valueStmt = entry.findProperty(entry.getModel().createProperty(PROPERTY.RDF_VALUE))
			
			if keyStmt and valueStmt and len(keyStmt) > 0 and len(valueStmt) > 0:
				key = Variant().parse(keyStmt[0])
				s = valueStmt[0]
				
				target_class = Tools().getResourceClass(s.getResource())
				if target_class is not None:
					try:
						value = target_class().parse(s.getResource())
					except:
						print "Unable to interpret seas:value as value for Parameter."
						traceback.print_exc()
						return
				elif s.getResource().model.is_list(s.getObject()):
					l = []
					s.getResource().model.parse_list(l, s.getObject())
					value = l
				else:
					value = Variant().parse(s)
				
				if key != None and value != None:
					self.map[key.getValue()] = value
				else:
					print "Null key or value found in map entry while parsing. Entry dropped.";
			else:
				print "Null key or value found in map entry while parsing. Entry dropped.";
				
			return

		# pass on to Object
		super(Map, self).parseStatement(statement)

