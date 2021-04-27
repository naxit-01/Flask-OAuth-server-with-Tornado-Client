import tornado.ioloop
import tornado.web
import json
from models import *

g_ClientID="MrVDUUQ3rdOthdg0T8tvNm68"
g_ClientSecret="T7pKWd3hPYBnz7GLj7akMItPJq91NbGTTnIevUv269LaF0So"

g_port = 9999
#g_authSerHostPort = "http://127.0.0.1:5000/"
#docker edition
g_authSerHostPort ="http://172.25.0.1:5000/"

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
			'grant_type': 'authorization_code',
			'scope': 'profile',
			'code': code,
		}
		response = await post_request_with_files(str(g_authSerHostPort)+'oauth/token',data=files, ClientID=g_ClientID, ClientSecret=g_ClientSecret)
		#print("Access token ziskan: " +str(response.json()["access_token"]))
		print("Access token ziskan: " +str(response))

		access_token = response["access_token"]
		
		#smenit access token za data
		headers = {
			'Authorization': f"Bearer {access_token}",
		}

		response = await get_request_with_headers(str(g_authSerHostPort) + 'api/me', data=headers)
		
		print("Data o uzivateli ziskana: " +str(response))
		data = {"username":response["username"],  "access_token":access_token}

		self.redirect(tornado.httputil.url_concat('mainPage', data))

class mainPage(tornado.web.RequestHandler):
	def get(self):
		self.render("html/afterLog.html", title="FirSer-Uvodni strana", data=self)
	async def post(self):
		if self.get_argument("logOut_button", None) != None:
			print("logOut")

			data = {
				'access_token': self.get_argument("access_token"),
				'client_ID':g_ClientID,
			}
			jmeno_uzivatele= await get_request_with_params(str(g_authSerHostPort) + 'delete_AT', data)

			self.redirect('root')


application = tornado.web.Application([
	(r"/root",loginPage),
	(r"/", loginPage),
	(r"/afterLog", afterLog),
	(r"/mainPage", mainPage),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("FirSer running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
