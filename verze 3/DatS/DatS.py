from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.web

import urllib.parse
import requests
import json

g_port = 9999
g_IDport = 9998

'''**************************************************'''

class loginPage(tornado.web.RequestHandler):
	def get(self):
		self.render("DatS/html/loginPage.html")

	def post(self):
		#GET ask for request_token and user secret
		'''Proof that GET works'''
		url = "http://localhost:" + str(g_IDport) + "/get_request_token"
		my_request_token=requests.get(url)
		print(my_request_token)
		'''End of proof'''

		#write into database
		self.redirect("http://localhost:" + str(g_IDport))
		#POST send request_token and secret + return adress, posting into IDPro/authorize

		'''Proof that POST works'''
		url = "http://localhost:" + str(g_IDport) + "/authorize"
		_body = {'data':'transmitted string'}
		body = urllib.parse.urlencode(_body)
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(url, method='POST', headers=None, body=body)
		http_client.close()
		print("-DatS POST sent")
		'''End of proof'''

class afterLog(tornado.web.RequestHandler):
	def get(self):
		self.render("DatS/html/afterLog.html")

	def post(self):
		#GET change request token for access token
		print("Python me jebal za chybejici odsazeny blok, tak tisknu hovna")

application = tornado.web.Application([
	(r"/", loginPage),
	(r"/afterLog", afterLog),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("DatS running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
