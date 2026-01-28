from SmartAPI.common.PROPERTY import PROPERTY
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.model.Obj import Obj
from SmartAPI.rdf.Variant import Variant
from SmartAPI.common.Tools import Tools

from dateutil import parser
import datetime
from rdflib import XSD
import isodate
from isodate.duration import Duration
import traceback


class TemporalContext(Obj):

	def __init__(self, uri = None, start = None, end = None, during = None):
		Obj.__init__(self, uri)
		if start is not None:
			self.setStart(start)
		else:
			self.start = None
		if end is not None:
			self.setEnd(end)
		else:
			self.end = None
		self.duration = None
		if during is not None:
			self.setDuring(during)
		else:
			self.during = None
		self.setType(RESOURCE.TEMPORALCONTEXT)

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		if Tools.serializedObjs.has_key(self):
			return Tools.serializedObjs.get(self)		
		
		temporalContext = super(TemporalContext, self).serialize(model);
		
		# start
		if self.hasStart():
			temporalContext.addProperty(model.createProperty( PROPERTY.START ), self.getStart().serialize(model))

		# end
		if self.hasEnd():
			temporalContext.addProperty(model.createProperty( PROPERTY.END ), self.getEnd().serialize(model))

		# duration
		if self.hasDuration():
			temporalContext.addProperty(model.createProperty( PROPERTY.DURATION ), model.createTypedLiteral(isodate.duration_isoformat(self.getDuration()), XSD.duration))

		# during
		if self.hasDuring():
			temporalContext.addProperty(model.createProperty( PROPERTY.DURING ), model.createResource(self.getDuring()))

		return temporalContext


	def  parseStatement(self, statement):	
		# get predicate
		predicate = str(statement.getPredicate())

		# start
		if predicate == PROPERTY.START:
			self.setStart(Variant().parse(statement))
# 			s = statement.getObject().toPython()
# 			if s is not None and not isinstance(s, datetime.datetime):
# 				try:
# 					s = parser.parse(s)
# 				except:
# 					print "Unknown date format for TemporalContext start:", s
# 			self.setStart(s)
# 			return
			
		# end
		if predicate == PROPERTY.END:
			self.setEnd(Variant().parse(statement))
# 			e = statement.getObject().toPython()
# 			if e is not None and not isinstance(e, datetime.datetime):
# 				try:
# 					e = parser.parse(e)
# 				except:
# 					print "Unknown date format for TemporalContext end:", e
# 			self.setEnd(e)
# 			return
			
		# duration
		if predicate == PROPERTY.DURATION:
			try:
				self.setDuration(statement.getString())
			except:
				print "Unable to interpret seas:duration value as literal."
				traceback.print_exc() 
			return

		# during
		if predicate == PROPERTY.DURING:
			try:
				self.setDuring(statement.getResource().toString())
			except:
				print "Unable to interpret seas:during value as resource."
				traceback.print_exc()
			return
		
		# pass on to Object
		super(TemporalContext, self).parseStatement(statement)
		
	def hasStart(self):
		return self.start is not None
	
	def getStart(self):
		return self.start

	def setStart(self, start):
		'''
		@param start: it can be a Variant, datetime.date, datetime.time or datetime.datetime type,
		it can also be ISO8601 date-time string, like "2017-03-28T15:18:54.842"   
		'''
		if isinstance(start, Variant):
			self.start = start
		elif isinstance(start, str):
			self.start = Variant(isodate.parse_datetime(start))
		else:
			self.start = Variant(start)

	def hasEnd(self):
		return self.end is not None
	
	def getEnd(self):
		return self.end

	def setEnd(self, end):
		'''
		@param end: it can be a Variant, datetime.date, datetime.time, datetime.datetime type,
		it can also be string, which requires a valid ISO8601 date-time string, like "2017-03-28T15:18:54.842"   
		'''
		if isinstance(end, Variant):
			self.end = end
		elif isinstance(end, str):
			self.end = Variant(isodate.parse_datetime(end))
		else:
			self.end = Variant(end)

	def hasDuration(self):
		return self.duration is not None

	def getDuration(self):
		return self.duration

	def setDuration(self, *args):
		'''
        It can take either one single parameter, or six parameters.
        @param  : if one single parameter, then its type has to be either String or isodate.Duration type. If string, then
        the string has to align with ISO 8601 standard, with the format like "PnYnMnDTnHnMnS". 
        See: https://www.w3.org/TR/xmlschema-2/#duration
        
        If 6 parameters, then all of them need to be integers, representing years, months, days, hours, minutes, seconds.           
        '''
		args = list(args)
		try:
			if len(args)==1:
				duration = args[0]
				if isinstance(duration, Duration):
					self.duration = duration
				elif isinstance(duration, str) or isinstance(duration, unicode):				
					self.duration = isodate.parse_duration(duration)
				else:
					raise("wrong parameter type: "+type(duration))
			elif len(args)==6:
				self.duration = Duration(years=args[0], months=args[1], days=args[2], hours=args[3], minutes=args[4], seconds=args[5])
			else:
				raise("The number of parameters has to be either 1 or 6!")
		except:
			traceback.print_exc()	
			traceback.print_stack()   

	def hasDuring(self):
		return self.during is not None

	def getDuring(self):
		return self.during

	def setDuring(self, during):
		self.during = during
