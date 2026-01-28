from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.Tools import Tools
from SmartAPI.model.Activity import Activity
from SmartAPI.model.Obj import Obj

from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.types import *
from rdflib import XSD

import traceback

class Provenance(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.generatedBy = None
		self.generatedAt = None
		self.generationMethods = []
		self.dataSources = []
		self.props =[]
		self.setType(RESOURCE.PROVENANCE)
		
	def hasGeneratedBy(self):
		return self.generatedBy is not None
	
	def getGeneratedBy(self):
		return self.generatedBy
	
	def setGeneratedBy(self, _generatedBy):
		self.generatedBy = _generatedBy
		
	def hasGeneratedAt(self):
		return True
	
	def getGeneratedAt(self):
		return self.generatedAt
		
	def setGeneratedAt(self, _generatedAt):
		self.generatedAt = _generatedAt
		
	def hasGenerationMethod(self):
		return len(self.generationMethods) > 0
	
	def getGenerationMethods(self):
		return self.generationMethods
	
	def addGenerationMethod(self, generationMethod):
		if isinstance(generationMethod, Obj):
			self.generationMethods.append(generationMethod)
		else:
			self.generationMethods.append(Obj(generationMethod))
	
	def setGenerationMethods(self, _generationMethods):
		self.generationMethods = _generationMethods
		
	def hasDataSource(self):
		return len(self.dataSources) > 0
	
	def getDataSources(self):
		return self.dataSources
	
	def addDataSource(self, dataSource):
		if isinstance(dataSource, Obj):
			self.dataSources.append(dataSource)
		else:
			self.dataSources.append(Obj(dataSource))
			
	def setDataSources(self, _dataSources):
		self.dataSources = _dataSources
		
	def hasProperty(self):
		return len(self.props) > 0
	
	def getProperties(self):
		return self.props
	
	def addProperty(self, property):
		self.props.append(property)
		
	def setProperties(self, _properties):
		self.props = _properties
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		resource = super(Provenance, self).serialize(model)
	
		# generatedby
		if self.hasGeneratedBy():
			resource.addProperty( model.createProperty( PROPERTY.GENERATEDBY ), self.generatedBy.serialize(model) )

		# generatedat
		if self.hasGeneratedAt():
			resource.addProperty(model.createProperty( PROPERTY.GENERATEDAT ), model.createLiteral(self.getGeneratedAt()))
	
		# generationMethods
		for i in range(len(self.generationMethods)):
			resource.addProperty(model.createProperty( PROPERTY.GENERATIONMETHOD ), self.generationMethods[i].serialize(model))
	
		# dataSources
		for i in range(len(self.dataSources)):
			resource.addProperty(model.createProperty( PROPERTY.DATASOURCE ), self.dataSources[i].serialize(model))
	
		# props
		for i in range(len(self.props)):
			resource.addProperty( model.createProperty( PROPERTY.SMARTAPI_PROPERTY ), model.createResource( self.props[i]))
	
		return resource


	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# generatedby
			if predicate == PROPERTY.GENERATEDBY:
				try:
					self.setGeneratedBy(Activity().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:generatedBy value as resource."
					traceback.print_exc()
				return
		
			# generatedat
			if predicate == PROPERTY.GENERATEDAT:
				try:
					self.setGeneratedAt(statement.getObject().toPython())
				except:
					print "Unable to interpret seas:generatedAt value as date literal."
					traceback.print_exc()
				return
		
			# generationMethod
			if predicate == PROPERTY.GENERATIONMETHOD:
				try:
					self.addGenerationMethod(Obj().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:generationMethod value as resource."
					traceback.print_exc()
				return
		
			# dataSource
			if predicate == PROPERTY.DATASOURCE:
				try:
					self.addDataSource(Obj().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:dataSource value as resource."
					traceback.print_exc()
				return
		
			# property
			if predicate == PROPERTY.SMARTAPI_PROPERTY:
				try:
					self.addProperty(statement.getResource().toString())
				except:
					print "Unable to interpret seas:property value as resource."
					traceback.print_exc()
				return
		
			# pass on to Obj
			super(Provenance, self).parseStatement(statement)

