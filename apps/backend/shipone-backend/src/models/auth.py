from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
from src.models.user import db

class Auth(db.Model):
    __tablename__ = 'auth'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamento com User
    user = db.relationship('User', backref=db.backref('auth_tokens', lazy=True))
    
    def __init__(self, user_id, token_hash, expires_at):
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
    
    @staticmethod
    def generate_token(user_id, secret_key):
        """Gera um token JWT para o usuário"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    
    @staticmethod
    def verify_token(token, secret_key):
        """Verifica se o token é válido"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

