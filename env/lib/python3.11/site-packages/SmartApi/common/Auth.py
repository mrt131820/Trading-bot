from SmartAPI.common.HttpClient import HttpClient
import traceback
import json
import urllib2

class Auth(object):
    
    @classmethod
    def oauth2AuthorizeApplication(cls, authorizationCallUri, clientId, scope):
        authorizationCode = None
        
        try:
            authorizationResponse = cls.sendRequest(authorizationCallUri + "?response_type=code&client_id=" + clientId + "&scope=" + scope, "")
            
            jo =  json.loads(authorizationResponse)
            authorizationCode = jo["code"]
            redirectUri = jo["redirect_uri"]
        except:
            traceback.print_exc()
            
        return authorizationCode
    
    @classmethod
    def oauth2AuthenticateUser(cls, autorizationCallUri, authorizationCode, userId, userSecret, redirectUri):
        ''' send a new request to SecurityServer that contains authorization
         code, client id and client secret (that has been registered separately to SecurityServer earlier)'''
        accessToken = ""
        try:
            tokenResponse = cls.sendRequest(autorizationCallUri + "?client_id=" + userId + "&client_secret=" + userSecret +
                                     "&grant_type=authorization_code&redirect_uri=" + redirectUri + "&code=" + authorizationCode, "")
            jo = json.loads(tokenResponse)
            accessToken = jo['access_token']
            
        except urllib2.HTTPError, e:
            print 'ERROR at oauth2AuthenticateUser(): ', str(e.reason), ' [code]: ', str(e.code)
            traceback.print_exc()
        except Exception:
            traceback.print_exc()
        
        return accessToken
    
    @classmethod
    def sendRequest(cls, uri, body):
        response, contentType = HttpClient().sendPost( uri, body, content_type = "application/json-rpc", accept_type = "application/json-rpc")
        return response