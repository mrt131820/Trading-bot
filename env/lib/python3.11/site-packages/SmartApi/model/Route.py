from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.Property import Property
from SmartAPI.model.Obj import Obj
from SmartAPI.model.Coordinates import Coordinates
from rdflib.namespace import RDF
from SmartAPI.common.Tools import Tools

import traceback


class Route(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.setType(RESOURCE.ROUTE)
		self.route_points = []
		self.length = None
		self.energyConsumption = None
		self.averageVelocity = None
		self.duration = None
	
	def hasRoutePoints(self):
		return len(self.route_points) > 0
	
	def getRoutePoints(self):
		return self.route_points
	
	def setRoutePoints(self, points):
		self.route_points = points
	
	def addRoutePoint(self, point):
		self.route_points.append(point);
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		route = super(Route, self).serialize(model)
		
		if self.hasRoutePoints():
			rdfList = model.createNudeList()
			rdfList.add_items(self.route_points)
			
			listContainer = model.createResource()
			listContainer.addProperty(Property(RDF.first), rdfList)
			
			route.addProperty(model.createProperty( PROPERTY.LIST ), listContainer)

		if self.hasLength():
			route.addProperty(model.createProperty( PROPERTY.LENGTH ), self.length.serialize(model));
		
		if self.hasEnergyConsumption():
			route.addProperty(model.createProperty( PROPERTY.ENERGYCONSUMPTION ), self.energyConsumption.serialize(model));
		
		if self.hasAverageVelocity():
			route.addProperty(model.createProperty( PROPERTY.AVERAGEVELOCITY ), self.averageVelocity.serialize(model));
		
		if self.hasDuration():
			route.addProperty(model.createProperty( PROPERTY.DURATION ), self.duration.serialize(model));
		
		return route
	
	def parseStatement(self, statement):
		from SmartAPI.model.Velocity import Velocity
		from SmartAPI.model.ValueObject import ValueObject
		from SmartAPI.model.TemporalContext import TemporalContext
				
		# get predicate
		predicate = str(statement.getPredicate())

		# route points
		if predicate == PROPERTY.LIST:
			try:
				self.setRoutePoints(statement.getResource().toList(Coordinates))
			except:
				print "Unable to interpret seas:list value as a resource for Route."
				traceback.print_exc() 
			return
		
		
		if predicate == PROPERTY.LENGTH:
			try:
				self.setLength(ValueObject().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:length value as a resource for Route."
				traceback.print_exc() 
			return
		
		if predicate == PROPERTY.ENERGYCONSUMPTION:
			try:
				self.setEnergyConsumption(ValueObject().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:energyconsumption value as a resource for Route."
				traceback.print_exc() 
			return

		if predicate == PROPERTY.AVERAGEVELOCITY:
			try:
				self.setAverageVelocity(Velocity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:averageSpeed value as a resource for Route."
				traceback.print_exc() 
			return

		if predicate == PROPERTY.DURATION:
			try:
				self.setDuration(TemporalContext().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:duration value as a resource for Route."
				traceback.print_exc() 
			return
	
		# pass on to Object
		super(Route, self).parseStatement(statement)


	def hasLength(self):
		return self.length is not None
	
	def getLength(self):
		return self.length
	
	def setLength(self, l):
		self.length = l

	def hasEnergyConsumption(self):
		return self.energyConsumption is not None
	
	def getEnergyConsumption(self):
		return self.energyConsumption
	
	def setEnergyConsumption(self, l):
		self.energyConsumption = l

	def hasAverageVelocity(self):
		return self.averageVelocity is not None
	
	def getAverageVelocity(self):
		return self.averageVelocity
	
	def setAverageVelocity(self, l):
		self.averageVelocity = l
		
	def hasDuration(self):
		return self.duration is not None
	
	def getDuration(self):
		return self.duration
	
	def setDuration(self, l):
		self.duration = l
		
