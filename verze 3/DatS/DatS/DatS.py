from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.web
import aiohttp
import asyncio
import urllib.parse
import requests
import json

#TODO spojit do jednoho
from databaze import write_my_request_token
from databaze import read_my_request_token

g_port = 9999
g_IDport = 9998

'''**************************************************'''

class loginPage(tornado.web.RequestHandler):
	def get(self):
		self.render("html/loginPage.html")

	async def post(self):
		#GET ask for request_token and user secret
		url = "http://localhost:" + str(g_IDport) + "/get_request_token"
		data=await getHttp(url)
		write_my_request_token(data)
		print("loginPage: ziskany request_token: " + str(read_my_request_token()))

		self.redirect(tornado.httputil.url_concat("http://localhost:" + str(g_IDport), [("reqTok", read_my_request_token()), ("redirect_url", "http://localhost:" + str(9999) + "/afterLog")]))

class afterLog(tornado.web.RequestHandler):
	async def get(self):
		#changeRequestTokenForAccessToken
		url="http://localhost:" + str(g_IDport) + "/authorize"
		data = {
            'request_token': read_my_request_token(),
        }	
		print("afterLog: odeslany request token: "+str(read_my_request_token()))
		access_token= await make_request(url, data)
		print("afterLog: ziskany access token: "+str(access_token))
		
		#askDataWithAccessToken
		print("askDataWithAccessToken: ptam se na data")
		url="http://localhost:" + str(g_IDport) + "/get_users_data"
		data2 = {
            'access_token': access_token,
        }
		jmeno_uzivatele= await make_request(url, data2)

		#writePage
		#self.render("html/afterLog.html")
		self.write("Vitejte uzivateli: "+str(jmeno_uzivatele))

async def make_request(url, data):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=data) as resp:
                return await resp.text()
                
async def getHttp(url):
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				return await resp.text()

application = tornado.web.Application([
	(r"/", loginPage),
	(r"/afterLog", afterLog),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("DatS running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
