from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.Property import Property
from SmartAPI.rdf import List, OrderedList, LinkedList, ItemizedList, NudeList
from SmartAPI.model.Obj import Obj
from SmartAPI.model.Evaluation import Evaluation
from SmartAPI.model.SystemOfInterest import SystemOfInterest
from SmartAPI.model.TemporalContext import TemporalContext
from SmartAPI.rdf.List import List
from SmartAPI.common.Tools import Tools

import traceback

from rdflib import XSD
from rdflib.namespace import RDF
import SmartAPI


class TimeSeries(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.quantity = None
		self.unit = None
		self.timeStep = None
		self.list = None # its type is SmartAPI.rdf.List
		self.systemOfInterest = None
		self.temporalContext = None
		self.setType(RESOURCE.TIMESERIES)

	def serialize(self, model):
		'''
		Note self.list is always serialized as OrderedList, no matter what original type it is.
		'''
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		ts = super(TimeSeries, self).serialize(model);

		# quantity
		if self.hasQuantity():
			quantity = model.createResource(self.quantity)
			ts.addProperty(model.createProperty( PROPERTY.QUANTITYKIND ), quantity)
		
		# unit
		if self.hasUnit():
			unit = model.createResource(self.unit)
			ts.addProperty(model.createProperty( PROPERTY.UNIT ), unit)

		# timestep
		if self.hasTimeStep():
			ts.addProperty(model.createProperty( PROPERTY.TIMESTEP ), model.createTypedLiteral(self.getTimeStep(), XSD.duration))
	
		# list
		if self.hasList():	
			if (isinstance(self.list, OrderedList.OrderedList) or isinstance(self.list, ItemizedList.ItemizedList) or
			isinstance(self.list, NudeList.NudeList)):				
				listContainer = model.createResource()
				if self.list.hasBaseObject():								
					listContainer.addProperty(model.createProperty( PROPERTY.BASEOBJECT ), 
											self.list.getBaseObject().serialize(model))	
				# TODO: replace PROPERTY.ABSTRACT with rdf.first				
 				listContainer.addProperty(model.createProperty(PROPERTY.ABSTRACT), self.list)									 
				ts.addProperty(model.createProperty( PROPERTY.LIST ), listContainer)			 
			
			else: # Linkedlist								
				ts.addProperty(model.createProperty( PROPERTY.LIST ), self.list)
					
# 			rdfList = model.createOrderedList()
# 			if isinstance(self.list, list):			
# 				rdfList.add_items(self.list)
# 			elif isinstance(self.list, List):
# 				rdfList.add_items(self.list.elements)
# 			
# 			listContainer = model.createResource()
# 			listContainer.addProperty(Property(RDF.first), rdfList)
# 			
# 			ts.addProperty(model.createProperty( PROPERTY.LIST ), listContainer)

		# systemOfInterest
		if self.hasSystemOfInterest():
			ts.addProperty(model.createProperty( PROPERTY.SYSTEMOFINTEREST ), self.systemOfInterest.serialize(model))

		# temporalcontext
		if self.hasTemporalContext():			
			ts.addProperty(model.createProperty( PROPERTY.TEMPORALCONTEXT ), self.temporalContext.serialize(model))

		return ts;

	def parseStatement(self, statement):
					
			# get predicate
			predicate = str(statement.getPredicate())

			# quantity
			if predicate == PROPERTY.QUANTITYKIND:
				try:
					self.setQuantity(statement.getResource().toString())
				except:
					print "Unable to interpret seas:quantity value as resource."
					traceback.print_exc() 
				return
			
			# unit
			if predicate == PROPERTY.UNIT:
				try:
					self.setUnit(statement.getResource().toString())
				except:
					print "Unable to interpret seas:unit value as resource."
					traceback.print_exc() 
				return
			
			# timestep
			if predicate == PROPERTY.TIMESTEP:
				try:
					self.setTimeStep(statement.getString());
				except:
					print "Unable to interpret seas:timeStep value as literal string."
					traceback.print_exc() 
				return
			
			# list
			if predicate == PROPERTY.LIST:				
				try:	
					list_python, listType = statement.getResource().toList(Evaluation)									
					self.setList(list_python, listType)
				except:
					print "Unable to interpret seas:list value as resource."					
				return
			
			# systemofinterest
			if predicate == PROPERTY.SYSTEMOFINTEREST:
				try:
					self.setSystemOfInterest(SystemOfInterest().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:systemOfInterest value as resource."
					traceback.print_exc() 
				return
			
			# temporalcontext
			if predicate == PROPERTY.TEMPORALCONTEXT:
				try:
					self.setTemporalContext(TemporalContext().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:temporalContext value as resource."
					traceback.print_exc() 
				return
			
			# pass on to Object
			super(TimeSeries, self).parseStatement(statement)
		


	def hasQuantity(self):
		return self.quantity is not None

	def getQuantity(self):
		return self.quantity
	
	def setQuantity(self, quantity):
		self.quantity = quantity

	def hasUnit(self):
		return self.unit is not None

	def getUnit(self):
		return self.unit
	
	def setUnit(self, unit):
		self.unit = unit

	def hasTimeStep(self):
		return self.timeStep is not None
	
	def getTimeStep(self):
		return self.timeStep
	
	def setTimeStep(self, timeStep):
		self.timeStep = timeStep

	def hasList(self):
		return self.list is not None			
# 		if isinstance( self.list, List):
# 			return len(self.list.elements)>0
# 		else:
# 			return len(self.list) > 0
	
	def getList(self):
		return self.list

	def setList(self, li, listType='OrderedList'):
		'''
		@type li: seasobject.rdf.List or Python list
		'''		
		if isinstance(li, list):# if it is Python list
			if listType=='LinkedList':
				ol = LinkedList.LinkedList()
			elif listType == 'ItemizedList':
				ol = ItemizedList.ItemizedList()
			elif listType == 'NudeList':
				ol = NudeList.NudeList()
			else:
				ol = OrderedList.OrderedList()
				
			ol.add_items(li)
			self.list = ol
		elif isinstance(li, List):			
			self.list = li
		else:
			print 'ERROR: parameter to setList() has to be either Python list or SeasObject.rdf.List!'

	def addListItem(self, item):
		from SmartAPI.rdf.Variant import Variant
		if not isinstance(item, Variant) and not isinstance(item, Obj):
			item = Variant(item)
		if not self.hasList():
			self.setList(LinkedList.LinkedList())
		self.list.add_items(item)		

	def getListItem(self, index):
		return self.list.get_item(index)

	def getListSize(self):
		if not self.hasList():
			return 0
		else:
			return len(self.list.elements)
	
	def setBaseObject(self, baseObject):	
		if not self.hasList():
			self.setList(LinkedList.LinkedList())		
		self.getList().setBaseObject(baseObject)
	
	def getBaseObject(self):
		if self.hasList():
			return self.getList().getBaseObject()
		else:
			return None		

	def hasSystemOfInterest(self):
		return self.systemOfInterest is not None

	def getSystemOfInterest(self):
		return self.systemOfInterest

	def setSystemOfInterest(self, system):
		self.systemOfInterest = system

	def hasTemporalContext(self):
		return self.temporalContext is not None

	def getTemporalContext(self):
		return self.temporalContext

	def setTemporalContext(self, temporalContext):
		self.temporalContext = temporalContext
