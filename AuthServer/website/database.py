import time
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

db = SQLAlchemy()

class User(db.Model):
    '''Provides service for saved database users'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))
    
    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    '''
    def check_password(self, password): 
        return password == 'valid'
    '''

    def checkPassword(self, password):
        return self.password == password

class OAuth2Client(db.Model, OAuth2ClientMixin):
    '''Provides service for saved database clients'''
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    '''Provides service for saved database authorization codes (request tokens)'''
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    '''Provides service for saved database access tokens'''
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    '''
    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in
        return expires_at >= time.time()
    '''

    def delete_access_token(self, client_ID):
        '''Deletes access token from database'''
        if self.client_id == client_ID:
            db.session.delete(self)
            db.session.commit()
            return "valid"
        else:
            return "invalid"
