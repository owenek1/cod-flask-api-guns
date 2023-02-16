from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager

from resources import configure_resources
from cache import configure_cache
from config import FlaskConfiguration

def create_app():
  app = Flask(__name__)
  app.config.from_object(FlaskConfiguration)

  configure_cors(app)
  configure_marshmallow(app)
  configure_resources(app)
  configure_cache(app)
  configure_mongodb(app)
  configure_jwt(app)

  return app

def configure_cors(app):
  CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False", "expose_headers": ["X-Pagination"]}})

def configure_marshmallow(app: Flask):
  Marshmallow(app)

def configure_mongodb(app: Flask):
  MongoEngine(app)

def configure_jwt(app: Flask): 
  JWTManager(app)