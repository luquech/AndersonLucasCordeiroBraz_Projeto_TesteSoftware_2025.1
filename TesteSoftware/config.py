import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_super_segura'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///clinica.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False