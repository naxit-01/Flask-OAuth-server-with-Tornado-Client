import time
from flask import Blueprint, request, session, url_for
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .database import db, User, OAuth2Client, OAuth2Token
from .oauth2 import authorization, require_oauth

bp = Blueprint(__name__, 'home')

def current_user():
    '''Returns user in active session'''
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

def split_by_crlf(s):
    '''Helper function, split lines'''
    return [v for v in s.splitlines() if v]

@bp.route('/', methods=('GET', 'POST'))
def home():
    '''Home page, allows to log in or create account (account serves to register a client)'''
    if request.method == 'POST': # After pressing the button
        username = request.form.get('username')
        password = request.form.get('password')

        # Find an account if it exists
        user = User.query.filter_by(username=username).first()

        # Create a new account if it does not exist
        if not user:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['id'] = user.id

        # Check password for the existing account
        else:
            if user.checkPassword(password):
                session['id'] = user.id
                
        # If redirect is send, redirect to it | otherwise load page again with logged account
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')

    # Get information about the account
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []

    return render_template('home.html', user=user, clients=clients)

@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    '''Handles client creation under an account'''
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')

    client_id = gen_salt(24) # Generate unique client ID
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )

    # Collect information from html form
    form = request.form
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)

    # Decide if client needs client secret
    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    # Add client into database
    db.session.add(client)
    db.session.commit()
    return redirect('/')

@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    '''Authorize user on clients request'''
    user = current_user()
    if not user: # If no user is logged in, let it logg in through main page
        return redirect(url_for('website.routes.home', next=request.url))

    if request.method == 'GET': # Provide user with desired page
        try:
            grant = authorization.validate_consent_request(end_user=user) # Decise what grant is client (server) asking for
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant) # Offer user to validate the grant
    
    if not user and 'username' in request.form: # Find user, if request was send as POST
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()

    if request.method=='POST': # Action after button was pushed
        if 'submit_button' in request.form: # Return to client with consent, if it was given
            if request.form['confirm']:
                grant_user = user
            else:
                grant_user = None
            return authorization.create_authorization_response(grant_user=grant_user)

        if 'changeuser_button' in request.form: # If user wants to log as someone else, redirect him to main login page
            del session['id']
            return redirect(url_for('website.routes.home', next=request.url))

@bp.route('/logout')
def logout():
    '''Delete session if someone loggs out'''
    del session['id']
    return redirect('/')

@bp.route('/delete_AT')
def delete_AT():
    '''Delete access token, if request was sent'''
    accessToken = request.args.get('access_token')
    clientID = request.args.get("client_ID")
    token = OAuth2Token.query.filter_by(access_token=accessToken).first() # Finds token in database
    return token.delete_access_token(clientID)

@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    '''Issue access token'''
    return authorization.create_token_response()

'''
@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')
'''

@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    '''Returns requested user information in json format'''
    user = current_token.user
    return jsonify(id=user.id, username=user.username)
