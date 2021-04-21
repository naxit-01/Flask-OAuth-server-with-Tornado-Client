
from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.web
import aiohttp

import requests
import asyncio
import urllib.parse
import json

g_port = 9999
g_ClientID="ywnGz6l7cah6KPNglP92vNCD"
g_ClientSecret="SKQcQSJiaI35wdHLe6o0DABJljsGuql0I1fLtWMnBBhl9ktn"

'''**************************************************'''

class loginPage(tornado.web.RequestHandler):
	def get(self):
		self.render("html/loginPage.html")

	async def post(self):
		if self.get_argument("authSer_button", None) != None:
			self.redirect(tornado.httputil.url_concat("http://127.0.0.1:5000/oauth/authorize", 
			[("response_type", "code"), 
			("client_id", g_ClientID),
			("scope","profile")]))
			
		if self.get_argument("googleAuth_button", None) != None:
			self.redirect('root')
		

class afterLog(tornado.web.RequestHandler):
	async def get(self):

		#smenit code z url za access token
		code = self.get_query_argument("code")
		print("Kod ziskan "+str(code))

		files = {
			'grant_type': (None, 'authorization_code'),
			'scope': (None, 'profile'),
			'code': (None, code),
		}

		response = requests.post('http://127.0.0.1:5000/oauth/token', files=files, auth=(g_ClientID, g_ClientSecret))
		
		#print("Access token ziskan: " +str(response.json()["access_token"]))
		print("Access token ziskan: " +str(response.json()))

		access_token = response.json()["access_token"]
		
		#smenit access token za data
		headers = {
			'Authorization': f"Bearer {access_token}",
		}

		response = requests.get('http://127.0.0.1:5000/api/me', headers=headers)

		print("Data o uzivateli ziskana: " +str(response.json()))
		data = {"username":response.json()["username"],  "access_token":access_token}

		self.redirect(tornado.httputil.url_concat('mainPage', data))

class mainPage(tornado.web.RequestHandler):
	def get(self):
		self.render("html/afterLog.html", title="FirSer-Uvodni strana", data=self)
	async def post(self):
		if self.get_argument("logOut_button", None) != None:
			print("logOut")

			data2 = {
				'access_token': self.get_argument("access_token"),
				'client_ID':g_ClientID,
			}
			jmeno_uzivatele= await make_request('http://127.0.0.1:5000/delete_AT', data2)

			self.redirect('root')

		if self.get_argument("nothing_button", None) != None:
			#ztrati vsechny argumenty - neuzitecny button
			data=self.json()
			self.redirect('mainPage')

async def make_request(url, data):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=data) as resp:
                return await resp.text()
                
async def getHttp(url):
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				return await resp.text()

application = tornado.web.Application([
	(r"/root",loginPage),
	(r"/", loginPage),
	(r"/afterLog", afterLog),
	(r"/mainPage", mainPage),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("DatS running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
