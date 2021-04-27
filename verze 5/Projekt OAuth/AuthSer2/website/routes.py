import time
from flask import Blueprint, request, session, url_for
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .models import db, User, OAuth2Client, OAuth2Token
from .oauth2 import authorization, require_oauth


bp = Blueprint(__name__, 'home')

#vraci bud aktivniho uzivatele nebo nic
def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

#rozdeluje podle radku
def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@bp.route('/', methods=('GET', 'POST'))
def home():
    
    #zmacknuti buttonu
    if request.method == 'POST':

        #ziskavani informaci z forms
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        #pokud username neexistuje tak ho vytvorit
        if not user:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['id'] = user.id

        #jinak zkontrolovat heslo    
        else:
            if user.checkPassword(password):
                session['id'] = user.id
                
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')

    #pro vytisk informaci o clientu v html
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []

    return render_template('home.html', user=user, clients=clients)


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')

    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )

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

    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    
    #nacist aktualniho uzivatele
    user = current_user()
    # if user log status is not true (Auth server), then to log it in   
    #pokud neni v session ulozeny zadny user
    if not user:
        #direktuje na home stranku pro prihlaseni uzivatele ale bere si s sebou data od clienta
        return redirect(url_for('website.routes.home', next=request.url))

    #pokud byla zavolana metoda GET
    if request.method == 'GET':
        
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()

    #pokud byla zavolana metoda POST
    if request.method=='POST':
        if 'submit_button' in request.form:
            if request.form['confirm']:
                grant_user = user
            else:
                grant_user = None
            return authorization.create_authorization_response(grant_user=grant_user)
        if 'changeuser_button' in request.form:
            del session['id']
            return redirect(url_for('website.routes.home', next=request.url))


@bp.route('/logout')
def logout():
    del session['id']
    return redirect('/')

@bp.route('/delete_AT')
def delete_AT():
    print("BP.ROUTE: DEF DELETE_AT")
    accessToken = request.args.get('access_token')
    clientID = request.args.get("client_ID")
    print("DELETE_AT: ZISKANO: access_token "+ str(accessToken)+ " a clientID "+str(clientID))
    token = OAuth2Token.query.filter_by(access_token=accessToken).first()
    return token.delete_access_token(clientID)


@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    print("PB.ROUTE oauth/token: DEF issue_token")
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)
