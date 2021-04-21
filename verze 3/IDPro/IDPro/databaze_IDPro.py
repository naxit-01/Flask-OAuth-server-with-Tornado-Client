database=[]
uzivatel=[]
uzivatel2=[]

def NaplnDatabazi():
	uzivatel.append("naxit")   
	uzivatel.append("koleno")
	uzivatel.append("")
	uzivatel.append("")
	uzivatel2.append("naxit2")
	uzivatel2.append("koleno2")
	uzivatel2.append("")
	uzivatel2.append("")

	database.append(uzivatel)
	database.append(uzivatel2)

def checkUser(user_name, password):
	#check with database
	print("checkUser kontroluje: "+ str(user_name))
	

	for i in range(len(database)):
		if (database[i][0]==user_name):
			print("uzivatel "+str(user_name)+" je v databazi")
			if(database[i][1]==password): 
				print("uzivatel "+str(user_name)+" zadal spravne heslo")
				return True
			else:
				print("uzivatel "+str(user_name)+" neni v databazi")
				return False

	print("uzivatel "+str(user_name)+" neni v databazi")
	return False

def writeAccessToken(user_name,access_token):
	for i in range(len(database)):
		if (database[i][0]==user_name):
			database[i][3]=access_token
			break
def writeRequestToken(user_name,request_token):
	for i in range(len(database)):
		if (database[i][0]==user_name):
			database[i][2]=request_token
			break

def odevzdatData(access_token):
	for i in range(len(database)):
		if (database[i][3]==access_token):		
			return str(database[i][0])
	return "Pristup byl odepren"

def odevzdatAccessToken(request_token):
	for i in range(len(database)):
		if (database[i][2]==request_token):
			return str(database[i][3])
	return "Pristup byl odepren"

def tiskDatabaze():
	for i in range(len(database)):
		print(str(database[i][0]),str(database[i][1]),str(database[i][2]),str(database[i][3]))
