from settings import Settings as settings
import datetime

class FlaskConfiguration:
  ENV = "development"
  DEBUG = ENV == "development"
  API_TITLE = settings.app_name
  API_VERSION = settings.app_version

  MONGODB_SETTINGS = {
    'host': 'mongodb+srv://cluster0.ur0zv.mongodb.net/restAPIWeapons',
    'username' : 'admin',
    'password' : 'owenek',
    'port': 27017
  }
  
  JWT_SECRET_KEY = '44ec03172fd2120bef67e5cf'
  JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
  JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)
  JWT_ERROR_MESSAGE_KEY = "message"

  API_SPEC_OPTIONS = {
      "info": {"title": API_TITLE, "description": settings.app_description},
  }