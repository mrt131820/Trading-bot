#!/usr/bin/python

""" 
"""

import sys
import json
import urllib, urllib2
import datetime
from pytz import timezone
from urlparse import urlparse


class Agent(object):
    def __init(self):
        pass
        
    def runQuery(self, server_uri, content_type, accept_type, payload):
        headers = { "content-type" : content_type, 'accept': accept_type }
        try:
            req = urllib2.Request(server_uri, payload, headers)
            # use a 5s timeout
            filehandle = urllib2.urlopen(req, timeout = 5)
            if filehandle is not None:
                data = filehandle.read()
                result = data
        except:
            print "Failed in contacting", server_uri
            print sys.exc_info()[1]
            result = None
        finally:
            return result
    