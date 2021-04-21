import tornado.ioloop
import tornado.web

g_port = 8888

class loginPage(tornado.web.RequestHandler):
	def get(self):
		form = """
			<title>Identity Provider</title>
			<h2>Login Page</h2><br>
			<form method="post">
				<label><b>User Name:</b></label>
					<input type="text" name="user_name"/>
				<br><br>
				<label><b>Password:</b></label>
					<input type="Password" name="password"/>
				<br><br><br>
				<input type="submit" value="Login"/>
			</form>
		"""
		self.write(form)

	def post(self):
		user_name = self.get_argument('user_name')
		password = self.get_argument('password')
		if(checkUser(user_name, password) == True):
			token = generateToken()
			print(user_name, password, token)
			self.write("Redirecting back...")
			#sent data to oauth
		else:
			#Ask to fill credentials again
			print("Not Authorized")

def checkUser(name, password):
	#check with database
	return True

def generateToken():
	return "j85j3nsdc.]xd46tjgd]d]fb]4"

application = tornado.web.Application([
	(r"/", loginPage),
])

if __name__ == "__main__":
	application.listen(g_port)
	print("Server running on port: " + str(g_port) + "...")
	tornado.ioloop.IOLoop.instance().start()
