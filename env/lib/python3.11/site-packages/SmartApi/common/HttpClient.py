import urllib, urllib2
from urlparse import urlparse
from SmartAPI.common.RESOURCE import RESOURCE
from SmartAPI.common.SERIALIZATION import SERIALIZATION
import sys
import traceback

class HttpClient(object):
	SMARTAPI_METHOD_REQUEST = "Request"
	SMARTAPI_METHOD_RESPONSE = "Response"
	SMARTAPI_METHOD_COMMAND = "Command"
	smartapiId = 0
	
	def __init__(self):
		self.debug = False
	
	def debugMode(self, flag):
		self.debug = flag
			
	def sendPost(self, server_uri, payload, content_type = "text/turtle", accept_type = "text/turtle", **otherHeaders):
		'''
		return two items: response message body, and content-type header
		'''	
		HttpClient.smartapiId += 1	
		body = ""
		contentType = ''
		headers = { "content-type" : content_type, 'accept': accept_type, "X-SmartAPI-CallId": str(HttpClient.smartapiId) }
		for name, value in otherHeaders.items():
			headers[name] = value
		
		if self.debug:
			print '\n HTTP POST request to ', server_uri
			print payload, '\n'
		try:
			req = urllib2.Request(server_uri, payload, headers)
			# use a 5s timeout
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				body = filehandle.read()
				headers = filehandle.info().headers
		except urllib2.HTTPError, e:
			print 'HTTPError --- ', str(e.reason),' Code: ', str(e.code)
			# raise this error up in order to handle it.
			raise e
		except urllib2.URLError:
			traceback.print_exc()
 		
 		if self.debug:
 			print '\n Response for HTTP POST:'
 			print response
 			
 		return body, headers

 	def sendPostWithRequest(self, server_uri, request_obj, serialization=SERIALIZATION.getMimeType(SERIALIZATION.TURTLE)):
 		''' 	
 		It serializes Request message into a string (no MIME headers) and send out via HTTP POST. Then 
 		it parses received response message into Response object.
 		Note: this function assumes HTTP server generates Smart API Response string in payload without MIME header 
 			 		
 		@param server_uri: uri string of the remote server 
 		@param request_obj: Request object
 		@return Response object 
 		'''
 		from SmartAPI.common.Tools import Tools
 		
 		payload, content_type = Tools.serializeRequest(request_obj, serialization) 		
 		response_body, response_headers = self.sendPost(server_uri, payload, content_type = content_type) 		
 		
 		resp = Tools.parseResponse(response_body, content_type)
 		return resp

	def sendGet(self, server_uri):
		body = ""
		try:
			req = urllib2.Request(server_uri)
			# use a 5s timeout
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				body = filehandle.read()
				headers = filehandle.info().headers
		except:
			print "Failed in contacting", server_uri
			print sys.exc_info()[1]
 			response = None
 		
		return body, headers
	
	def _findHTTPInterfaceUri(self, entity, activity):
		from SmartAPI.factory.Factory import Factory
		
		uri = ''
		if activity is not None:
			ia = activity.getHTTPInterface()
			if ia is not None:
				uri = ia.getInterfaceUri()
				return uri
		if uri == '':
			uri = Factory.createStandardInterface(entity.getDomain()).getInterfaceUri()
		return uri
		
	def makeStandardRequest(self, method, entity, temporalContext, timeSeries, serviceUri, publicKey, *valueObjects):
		'''
		@return: Activity
		'''
		from SmartAPI.factory.Factory import Factory
		from SmartAPI.common.Tools import Tools
		from SmartAPI.model.Response import Response
		
		req = Factory.createRequest(publicKey, method, Factory.defaultIdentity, entity, temporalContext, timeSeries, *valueObjects)
		# from the object, find activity that is for the required method and that supports most of the valueObjects 
		a = Tools.getMostCommonActivity(method, False, entity, *valueObjects)
		if serviceUri is None:
			serviceUri = self._findHTTPInterfaceUri(entity, a)
		resp = None
		try:
			resp, headers = self.sendPost(serviceUri, Tools.toString(req), seasMethod=self.SMARTAPI_METHOD_REQUEST)	
			
			resp = Response.fromString(resp, 'text/turtle')
		
			if resp.hasActivity():
				if resp.firstActivity().hasEntity():
					return resp.firstActivity()
				else:
					return None
		except:
			print "object request with HTTP client failed. Method: ", method
			traceback.print_exc()
			return None
		
	def getObject(self, entity, serviceUri=None, temporalContext=None, publicKey=None):
		'''
		@return: Activity
		'''
		return self.makeStandardRequest(RESOURCE.READ, entity, temporalContext, None, serviceUri, publicKey)
			
	def getValueObject(self, entity, serviceUri=None, temporalContext=None, publicKey=None, *valueObjects):	
		'''
		@return: Activity
		'''	
		return self.makeStandardRequest(RESOURCE.READ, entity, temporalContext, None, serviceUri, publicKey, *valueObjects)	
		
	def setObject(self, entity, serviceUri=None, timeSeries=None, publicKey=None):	
		'''
		@return: Activity
		'''
		return self.makeStandardRequest(RESOURCE.WRITE, entity, None, timeSeries, serviceUri, publicKey)
		
	def setValueObject(self, entity, serviceUri=None, timeSeries=None, publicKey=None, *valueObjects):
		'''
		@return: Activity
		'''
		return self.makeStandardRequest(RESOURCE.WRITE, entity, None, timeSeries, serviceUri, publicKey, *valueObjects)
	