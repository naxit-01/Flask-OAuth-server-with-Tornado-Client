from authlib.integrations.flask_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from .database import db, User
from .database import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    '''Class for handling Authorization Code Grant method (code equels request token)'''
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none',
    ]

    def save_authorization_code(self, code, request):
        '''Create client specific authorization code (request token), save it into database, return it back'''
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')

        # Create unique code from user and client information
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )

        # Save the code into database
        db.session.add(auth_code)
        db.session.commit()
        return auth_code

    def query_authorization_code(self, code, client):
        '''Return authorization code (request token) from datase if it exists and is not expired'''
        auth_code = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if auth_code and not auth_code.is_expired():
            return auth_code

    def delete_authorization_code(self, authorization_code):
        '''Delete authorization code (request token) from database'''
        db.session.delete(authorization_code)
        db.session.commit()
        
    def delete_access_token(self, accessToken):
        '''Delete access token from database'''
        db.session.delete(accessToken)
        de.session.commit()

    def authenticate_user(self, authorization_code):
        '''Check if provided authentication code (request token) is owned by the specific user'''
        return User.query.get(authorization_code.user_id)

'''
class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        print("DEF authenticate_refresh_token")
        token = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()
        if token and token.is_refresh_token_active():
            return token

    def authenticate_user(self, credential):
        print("DEF authenticate_user")
        return User.query.get(credential.user_id)

    def revoke_old_credential(self, credential):
        print("DEF revoke_old_credential")
        credential.revoked = True
        db.session.add(credential)
        db.session.commit()
'''

# Create functions for communicating with database
query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)
authorization = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)
require_oauth = ResourceProtector()


def config_oauth(app):
    '''Provides app configuration, defines which grant methods are supported'''
    authorization.init_app(app)

    # Grants
    #authorization.register_grant(grants.ImplicitGrant)
    #authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=True)])
    #authorization.register_grant(RefreshTokenGrant)

    # Revocation support
    '''
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)
    '''

    # Allows usage of bearer tokens (higher security than common ones)
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
