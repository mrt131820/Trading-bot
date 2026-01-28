from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Obj import Obj
from SmartAPI.common.Tools import Tools

from SmartAPI.rdf.Resource import Resource
from SmartAPI.rdf.types import *
from rdflib import XSD

import traceback

class Address(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.country = None
		self.city = None
		self.zipCode = None
		self.streetAddress = None
		self.setType(RESOURCE.ADDRESS)

	def hasCountry(self):
		return self.country is not None
	
	def getCountry(self):
		return self.country

	def setCountry(self, country):
		self.country = country

	def hasCity(self):
		return self.city is not None

	def getCity(self):
		return self.city

	def setCity(self, city):
		self.city = city

	def hasZipCode(self):
		return self.zipCode is not None

	def getZipCode(self):
		return self.zipCode

	def setZipCode(self, zipCode):
		self.zipCode = zipCode

	def hasStreetAddress(self):
		return self.streetAddress is not None

	def getStreetAddress(self):
		return self.streetAddress

	def setStreetAddress(self, streetAddress):
		self.streetAddress = streetAddress

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)			
		
		resource = super(Address, self).serialize(model)
	
		# country name
		if self.hasCountry():
			resource.addProperty(model.createProperty( PROPERTY.COUNTRY_NAME ), self.country)
		
		# locality
		if self.hasCity():
			resource.addProperty(model.createProperty( PROPERTY.LOCALITY ), self.city)
		
		# postal code
		if self.hasZipCode():
			resource.addProperty(model.createProperty( PROPERTY.POSTAL_CODE ), self.zipCode)
		
		# street address
		if self.hasStreetAddress():
			resource.addProperty(model.createProperty( PROPERTY.STREET_ADDRESS ), self.streetAddress)

		return resource


	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# country
			if predicate == PROPERTY.COUNTRY_NAME:
				try:
					self.setCountry(statement.getString());
				except:
					print "Unable to interpret vcard:country-name value as literal string."
					traceback.print_exc()
				return
	
			# city
			if predicate == PROPERTY.LOCALITY:
				try:
					self.setCity(statement.getString())
				except:
					print "Unable to interpret vcard:locality value as literal string."
					traceback.print_exc()
				return
	
			# street-address
			if predicate == PROPERTY.STREET_ADDRESS:
				try:
					self.setStreetAddress(statement.getString())
				except:
					print "Unable to interpret vcard:street-address value as literal string."
					traceback.print_exc()
				return
	
			# zipcode
			if predicate == PROPERTY.POSTAL_CODE:
				try:
					self.setZipCode(statement.getString())
				except:
					print "Unable to interpret vcard:postal-code value as literal string."
					traceback.print_exc()
				return
	
			# pass on to Object
			super(Address, self).parseStatement(statement)
	
