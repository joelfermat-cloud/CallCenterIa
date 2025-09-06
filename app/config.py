import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    APP_NAME  = os.getenv('APP_NAME', 'callcenter-ia')
    ENV       = os.getenv('ENV', 'dev')
    PORT      = int(os.getenv('PORT', '5000'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
