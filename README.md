### Project OAuth
Project OAuth provides an implementation of Flask OAuthorization server using Authlib. We also provide our own sample Client in python/tornado. It can be used in regular environment, but the main usage is implemented using docker.
You can quick start the project by running compose.bat. You can then open your browser on adress http://localhost:9999 to connect to the Client_sample. Authorization server runs on http://localhost:5000. There are sample users: user1, user2, user3 - all with password "user".

## Guide for connecting other clients
Before any connection can take place, you need to register the client in authorization server. Run it and open your browser with http://127.0.0.1:5000. Logg in with any name and proceed to registration. If you do not understand the options, read about OAuth protocol. Currently implemented grant type is authorization_code with response type code. Our sample client is allowed scope: profile. After you register, be sure to save client ID and client secret.

# Flow example
1. Redirect to http://localhost:5000/oauth/authorize
with response_type, client_id and scope as URL parameters. It equals to the values you registered. Authorization server has your redirect URL, which you also registered, and will redirect back to your server, when it is done with user login. If user login is successful, you will receive a code as part of the redirect URL. The code equals to term request token.
2. Make a POST request to http://172.16.238.1:5000/oauth/token (if you are using docker)
The request must contain ClientID, ClientSecret and data. Data is a dictionary structure containing grant_type, scope and code, received via the URL. The response to this request is an access token.
3. Get user data with GET on http://172.16.238.1:5000/api/me
You need to add data, dictionary structure containing the access token in format: 'Authorization': f"Bearer {access_token}".
4. To log the user out send GET to http://172.16.238.1:5000/delete_AT
with data containing access_token and client_ID. This will delete the token in the database of authorization server. If you need to access user data again, the user will have to provide his consent again and new token will be given to him.

The flow is presented in the Client_sample and you may use it as a reference.

5. If you connected your own client to the authorization server, delete the sample client and its users from the database. Not doing so, creates a huge security risk!

## File system
The project is made of two web servers, open authentication server and sample client server.

# Auth Server
This server is written in flask. The flask application is setup in app.py and works with code from the website folder. Aside from website, there are templates and static folders, containing html and css files. There is also an sqlite database.
The website folder contains additional moduls for the app and default setting in settings.py. Database.py deals with sqlite database, routes.py handles html requests and oauth2.py uses autlib to provide secure grant types.

# Sample Client Server
It is written in python/tornado. Most of it is written in main.py. The only modul is in the moduls folder and handles html requests asynchronously. Templates folder contains html files.

## Configuration
If you want to configure the flask server, your options are shown in app.py. Basically, you can add configuration to the default configuration file settings.py, set environmental variables or create your own configuration file.

## Other Grant types
The current version (as of spring 2021) works with Authorization Code Grant. Other grants are allowed, but are not implemented. If you want to add them, create a new class in oauth2.py.

## Refresh token
The refresh token grant is currently not functional. If you want to use it, uncomment appropriate parts (in most of the .py files) and make a request from your client.

## Running outside docker
It is possible to run both servers outside of docker, but you will need to change IP adresses first. Authorization server adress is configured in app.py, at the very bottom. In the sample client server, change global variables in main.py.