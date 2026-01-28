import sys
import os
import base64
import binascii
import traceback
import urllib2
import StringIO
import Crypto
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512
from SmartAPI.smartapiexceptions.UploadException import UploadException
from SmartAPI.smartapiexceptions.RevokeException import RevokeException
from SmartAPI.smartapiexceptions.NotAuthorizedException import NotAuthorizedException
from SmartAPI.smartapiexceptions.KeyAlreadyExistsOnServerException import KeyAlreadyExistsOnServerException


class SmartAPICrypto:
	def __init__(self,  k=16):
		self.k = k
	
	def symmetricEncrypt(self, key, text):
		try :
			iv = os.urandom(16)
			aesCipher = AES.new(key, AES.MODE_CBC, iv)
			cipherText = aesCipher.encrypt(self.PKCS7pad(text))
			
			return base64.b64encode(iv) + base64.b64encode(cipherText)
		except:
			print "Symmetric encryption failed:", sys.exc_info()[1]
			traceback.print_exc()
			return None
	
	def symmetricDecrypt(self, key, text):
		decodedIv = base64.b64decode(text[0:24])
		decodedContent = base64.b64decode(text[24:])
		
		try :
			aesCipher = AES.new(key, AES.MODE_CBC, decodedIv)
			return self.PKCS7strip(aesCipher.decrypt(decodedContent))
		except:
			print "Symmetric decryption failed:", sys.exc_info()[1]
			traceback.print_exc()
			return None
		
	def asymmetricEncrypt(self, pubKey, text):
		try :
			# 16 bytes = 128 bits
			aesKey = self.generateSymmetricKey()
			iv = os.urandom(16)
			aesCipher = AES.new(aesKey, AES.MODE_CBC, iv)
			pkcsCipher = PKCS1_OAEP.new(pubKey)
			cipherText = aesCipher.encrypt(self.PKCS7pad(text))
			keyText = pkcsCipher.encrypt(aesKey)

			return base64.b64encode(keyText) + "\n" + base64.b64encode(iv) + base64.b64encode(cipherText), aesKey
		except:
			print "Encryption failed:", sys.exc_info()[1]
			traceback.print_exc()
			return None
	
	def asymmetricDecrypt(self, privKey, text):
		keyEnd = text.find('\n')
		
		decodedKey = base64.b64decode(text[0:keyEnd])
		decodedIv = base64.b64decode(text[keyEnd+1:keyEnd+25])
		decodedContent = base64.b64decode(text[keyEnd+25:])
		
		try :
			pkcsCipher = PKCS1_OAEP.new(privKey)
			decryptedKey = pkcsCipher.decrypt(decodedKey)
			aesCipher = AES.new(decryptedKey, AES.MODE_CBC, decodedIv)
			return self.PKCS7strip(aesCipher.decrypt(decodedContent)), decryptedKey
		except:
			print "Decryption failed:", sys.exc_info()[1]
			traceback.print_exc()
			return None, None
	
	def generateSymmetricKey(self):
		return Random.new().read(16)
	
	def generateKeyPair(self, algorithm = "RSA", keySize = 2048):
		"""
		Generate an RSA keypair with an exponent of 65537 and key size as in input parameters
		"""
		new_key = RSA.generate(keySize, e=65537)
		return new_key, new_key.publickey()
	
	def encryptAndEncodeKey(self, pubKey, symmetricKey):
		pkcsCipher = PKCS1_OAEP.new(pubKey)
		keyText = pkcsCipher.encrypt(symmetricKey)
		return base64.b64encode(keyText)
	
	def decryptAndDecodeKey(self, privKey, encodedKey):
		decodedKey = base64.b64decode(encodedKey)
		pkcsCipher = PKCS1_OAEP.new(privKey)
		return pkcsCipher.decrypt(decodedKey)
	
	def sign(self, privKey, dataBytes):
		# create a signature for the bytes
		hash = SHA512.new(dataBytes)
		pkcs = PKCS1_v1_5.new(privKey)
		signatureBytes = pkcs.sign(hash)
		return base64.b64encode(signatureBytes)
	
	def verifySignature(self, signature, pubKey, dataBytes):
		signatureBytes =  base64.b64decode(signature)
		pkcs = PKCS1_v1_5.new(pubKey)
		hash = SHA512.new(dataBytes)
		return pkcs.verify(hash, signatureBytes)
	
	def extractPemFormatPrivateKey(self, key, algorithm):
		if (algorithm == "RSA"):
			return RSA.importKey(key)
		return None
		
	def extractPemFormatPublicKey(self, key, algorithm):
		if (algorithm == "RSA"):
			return RSA.importKey(key)
		return None
	
	def convertPublicKeyToPemFormat(self, pubKey):
		return pubKey.exportKey("PEM")
	
	def convertPrivateKeyToPemFormat(self, privKey):
		return privKey.exportKey("PEM")
	
	def createEncodedMessageDigest(self, message):
		hash = SHA512.new(message).digest()
		return base64.b64encode(hash)
	
	def verifyEncodedMessageDigest(self, digest, message):
		computedDigest = self.createEncodedMessageDigest(message);
		return (digest == computedDigest)
	
	def loadPrivateKey(self, fileName):
		try:
			f = open(fileName,'r')
			return RSA.importKey(f.read())
		except:
			print "Could not find the private key or incorrect (non PEM) format"
		return None
	
	def downloadPublicKey(self, identifier, publicKeyServer):
		try:
			id = self.fetchKeyId(identifier, publicKeyServer)
			if (id < 0):
				# unknown identifier
				return None
			
			url = "%s/get/%s/"%(publicKeyServer, id)
			req = urllib2.Request(url)
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				data = filehandle.read()
				return self.extractPemFormatPublicKey(data, "RSA");
		except:
			print "Error in public key download:", sys.exc_info()[1]
		return None
	
	def uploadPublicKey(self, pubKey, myIdentifier, publicKeyServer, userName, password):
		responseCode = 0
		try:
			if not isinstance(pubKey, str):
				pubKeyString = self.convertPublicKeyToPemFormat(pubKey)
			else:
				pubKeyString = pubKey
			auth = base64.b64encode(b"%s:%s"%(userName, password)).decode("ascii")
			# post payload to key server
			url = "%s/add/"%(publicKeyServer)
			headers = { "content-type" : "text/plain", 'Authorization' : 'Basic %s' %  auth }
			req = urllib2.Request(url, myIdentifier + "\n" + pubKeyString, headers)
			filehandle = urllib2.urlopen(req, timeout = 10)
			if filehandle is not None:
				data = filehandle.read()
				responseCode = filehandle.getcode()
		except urllib2.HTTPError as e:
			responseCode = e.code
		except:
			raise UploadException("Server connection failed.")
		
		if (responseCode == 200):
			return True
		if (responseCode == 401 or responseCode == 403):
			raise NotAuthorizedException
		if (responseCode == 409):
			raise KeyAlreadyExistsOnServerException
		raise UploadException("Unknown error.")
	
	def revokePublicKey(self, identifier, publicKeyServer, userName, password):
		id = self.fetchKeyId(identifier, publicKeyServer)
		if (id < 0):
			# unknown identifier
			return False
		try:
			url = "%s/revoke/%s/"%(publicKeyServer, id)
			auth = base64.b64encode(b"%s:%s"%(userName, password)).decode("ascii")
			headers = { "content-type" : "text/plain", 'Authorization' : 'Basic %s' %  auth }
			req = urllib2.Request(url, None, headers)
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				data = filehandle.read()
				responseCode = filehandle.getcode()
		except urllib2.HTTPError as e:
			responseCode = e.code
		except:
			raise RevokeException("Server connection failed.")
		
		if (responseCode == 200):
			return True
		if (responseCode == 401 or responseCode == 403):
			raise NotAuthorizedException
		raise RevokeException("Unknown error.")
	
	def createAndSaveKeyPair(self, myIdentifier, privateKeyPath, publicKeyServer, username, password):
		priv, pub = self.generateKeyPair()
		pubStr = self.convertPublicKeyToPemFormat(pub)
		privStr = self.convertPrivateKeyToPemFormat(priv)
				
		with open(privateKeyPath, 'w') as f:
			f.write(privStr)
			
		self.uploadPublicKey(pubStr, myIdentifier, publicKeyServer, username, password)		
	
	def fetchKeyId(self, identifier, publicKeyServer):
		id = -1
		try:
			# get id from SERVER_URL/find/<identifier>
			url = "%s/find/%s/"%(publicKeyServer, identifier)
			req = urllib2.Request(url)
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				if filehandle.getcode() == 200:
					response = filehandle.read()
					return int(response[0:response.index(':')])
			return -1;
		except:
			return -1;

	def PKCS7strip(self, text):
		'''
		Remove the PKCS#7 padding from a text string
		'''
		nl = len(text)
		val = int(binascii.hexlify(text[-1]), 16)
		if val > self.k:
			raise ValueError('Input is not padded or padding is corrupt')

		l = nl - val
		return text[:l]
	
	def PKCS7pad(self, text):
		'''
		Pad an input string according to PKCS#7
		'''
		l = len(text)
		output = StringIO.StringIO()
		val = self.k - (l % self.k)
		for _ in xrange(val):
			output.write('%02x' % val)
		return text + binascii.unhexlify(output.getvalue())