import tornado.ioloop
import tornado.web
import json
from moduls import * # Contains a module for asynchronous requests

g_ClientID="MrVDUUQ3rdOthdg0T8tvNm68"
g_ClientSecret="T7pKWd3hPYBnz7GLj7akMItPJq91NbGTTnIevUv269LaF0So"

g_port = 9999
g_authServerPublic = "http://127.0.0.1:5000"
g_authServerDocker = "http://172.16.238.1:5000" # Adress for docker inner tunneling

'''**************************************************'''

class loginPage(tornado.web.RequestHandler):
	def get(self):
		self.render("templates/loginPage.html")

	def post(self):
		'''Redirect user to authorization server, you will receive a code (request token) in redirect URL'''
		if self.get_argument("authSer_button", None) != None:
			self.redirect(tornado.httputil.url_concat(g_authServerPublic + "/oauth/authorize", 
			[("response_type","code"), 
			("client_id",g_ClientID),
			("scope","profile")]))
			
		if self.get_argument("googleAuth_button", None) != None:
			self.write("This part has not been programmed yet.")
		

class afterLog(tornado.web.RequestHandler):
	async def get(self):
		'''Exchange code (request token) for access token, fetch user data'''
		code = self.get_query_argument("code")
		print("Acquired code: " + str(code))

		# Token exchange
		files = {
			'grant_type': 'authorization_code',
			'scope': 'profile',
			'code': code,
		}
		response = await post_request_with_files(g_authServerDocker + "/oauth/token", data=files, ClientID=g_ClientID, ClientSecret=g_ClientSecret)
		access_token = response["access_token"]
		print("Acquired access token: " + access_token)
		
		# Fetch user data
		headers = {
			'Authorization': f"Bearer {access_token}",
		}
		response = await get_request_with_headers(g_authServerDocker + "/api/me", data=headers)
		print("Data o uzivateli ziskana: " + str(response))

		data = {"username":response["username"],  "access_token":access_token}
		self.redirect(tornado.httputil.url_concat('mainPage', data))

class mainPage(tornado.web.RequestHandler):
	def get(self):
		self.render("templates/afterLog.html", title="Client Main Page", data=self)

	async def post(self):
		'''Log out and send a request to delete access token'''
		if self.get_argument("logOut_button", None) != None:
			print("logOut")

			data = {
				'access_token': self.get_argument("access_token"),
				'client_ID':g_ClientID,
			}
			await get_request_with_params(g_authServerDocker + '/delete_AT', data)

			self.redirect('/')

		if self.get_argument("nothing_button", None) != None:
			self.write("What did you expect? Told you, I do nothing.")

application = tornado.web.Application([
	(r"/", loginPage),
	(r"/afterLog", afterLog),
	(r"/mainPage", mainPage),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("Client_sample running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
