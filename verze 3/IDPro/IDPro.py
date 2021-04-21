from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.web

import urllib.parse
import requests
import json

g_port = 9998

#provizorni databaze
jmena=[]
hesla=[]
users_request_token=[]
users_access_token=[]
database={jmena,hesla,users_request_token,users_access_token}

'''**************************************************'''

class loginPage(tornado.web.RequestHandler):
	def get(self):
		self.render("IDPro/html/loginPage.html")

	def post(self):
		user_name = self.get_argument('user_name')
		password = self.get_argument('password')
		database[0].append(user_name)
		database[1].append(password)

		if(checkUser(user_name, password) == True):
			token = generateToken()
			#write token into database
			print("-IDPro inserted data + token: ")
			print(user_name, password, token)
			self.redirect("http://localhost:" + str(9999) + "/afterLog")
		else:
			#Ask to fill credentials again
			print("Not Authorized")

class authorize(tornado.web.RequestHandler):
	def post(self):
		'''Proof that post works'''
		print("-IDPro Received data: " + self.get_argument('data'))
		'''End of proof'''

		#fetch data from database and POST it to redirect adress, posting to DatS/afterLog

class get_request_token(tornado.web.RequestHandler):
	def get(self):
		self.write("request_token")
		print("request_token has been sent")
	
	def post(self):
		'''Proof that post works'''
		print("-IDPro Received data: " + self.get_argument('data'))
		'''End of proof'''
	

def checkUser(user_name, password):
	#check with database
	for i in database[0]:
		if(database[0][x]==user_name)
			return True
	return False

def generateToken():
	return "j85j3nsdc.]xd46tjgd]d]fb]4"

application = tornado.web.Application([
	(r"/", loginPage),
	(r"/authorize", authorize),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("IDPro running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
