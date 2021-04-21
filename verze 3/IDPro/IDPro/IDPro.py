from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
from tornado_sqlalchemy import SQLAlchemy

import urllib.parse
import requests
import json

#TODO spojit do jednoho
from databaze_IDPro import checkUser
from databaze_IDPro import NaplnDatabazi
from databaze_IDPro import writeRequestToken
from databaze_IDPro import writeAccessToken
from databaze_IDPro import odevzdatData
from databaze_IDPro import odevzdatAccessToken
from databaze_IDPro import tiskDatabaze

g_port = 9998

'''**************************************************'''

class loginPage(tornado.web.RequestHandler):
	def get(self):
		#self.render("IDPro/html/loginPage.html")
		self.render("html/loginPage.html")
		
	def post(self):
		user_name = self.get_argument('user_name')
		password = self.get_argument('password')
		request_token= self.get_query_argument("reqTok")
		redirect_url= self.get_query_argument("redirect_url")
		print("Ziskany request token: "+str(request_token))

		if(checkUser(user_name, password) == True):
			access_token = generateAccessToken()
			#write token into database
			#TODO check requestToken
			writeRequestToken(user_name,request_token)
			writeAccessToken(user_name,access_token)
			self.redirect(redirect_url)
		else:
			#Ask to fill credentials again
			print("Not Authorized")

class authorize(tornado.web.RequestHandler):
	def get(self):
		print("authorize: ziskany request token: "+str(self.get_argument('request_token')))
		print("authorize: odesilam access token: "+str(odevzdatAccessToken(self.get_argument('request_token'))))
		self.write(str(odevzdatAccessToken(self.get_argument('request_token'))))

class get_request_token(tornado.web.RequestHandler):
	def get(self):
		print("get_request_token: request token byl odeslan")
		self.write(generateRequestToken())

class get_users_data(tornado.web.RequestHandler):
	def get(self):
		print("ziskany_access_token: "+str(self.get_argument('access_token')))
		print("get_users_data: odesilam data: "+str(odevzdatData(self.get_argument('access_token'))))
		self.write(str(odevzdatData(self.get_argument('access_token'))))

def generateAccessToken():
	return "generated_access_token"

def generateRequestToken():
	return "generated_request_token"

application = tornado.web.Application([
	(r"/", loginPage),
	(r"/authorize", authorize),
	(r"/get_request_token", get_request_token),
	(r"/get_users_data", get_users_data),
])

if __name__ == "__main__":
	NaplnDatabazi()
	application.listen(g_port)
	print("IDPro running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
