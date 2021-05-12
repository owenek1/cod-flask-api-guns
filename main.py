from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from flask_cors import CORS

from flask_jwt_extended import JWTManager

import datetime

# Resources
from resources.home import Home
from resources.weapons import Weapons, WeaponsList
from resources.weaponTypes import WeaponTypes, WeaponTypesList
from resources.weaponAttachmentTypes import WeaponAttachmentTypes, WeaponAttachmentTypesList
from resources.weaponAttachments import WeaponAttachments, WeaponAttachmentsList
from resources.weaponBuilds import WeaponBuilds, WeaponBuildsList
from resources.users import UsersList, UsersLogin, UsersRegister, TokenRefresh, UsersProfile
from resources.secretResource import SecretResource
from resources.nightbots import NightbotRegister, NightbotUnregister

# Flask app configuration
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '44ec03172fd2120bef67e5cf'

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)
app.config['JWT_ERROR_MESSAGE_KEY'] = "message"

CORS(app)

jwt = JWTManager(app)

# Mongo DB
mongo_db_uri = "mongodb+srv://admin:owenek@cluster0.ur0zv.mongodb.net/restAPIWeapons?retryWrites=true&w=majority"
mongo = PyMongo(app, uri=mongo_db_uri)
db = mongo.db

# DB collections
app.config['DB_COLLECTIONS'] = db

# DB collections for resources
WeaponAttachmentTypes.weaponAttachmentTypesCollection = db.weaponAttachmentTypes
WeaponAttachmentTypesList.weaponAttachmentTypesCollection = db.weaponAttachmentTypes

WeaponAttachments.weaponAttachmentsCollection = db.weaponAttachments
WeaponAttachments.weaponsCollection = db.weapons

WeaponAttachmentsList.weaponAttachmentsCollection = db.weaponAttachments
WeaponAttachmentsList.weaponsCollection = db.weapons
WeaponAttachmentsList.weaponAttachmentTypesCollection = db.weaponAttachmentTypes

WeaponBuildsList.weaponBuildsCollection = db.weaponBuilds
WeaponBuildsList.weaponsCollection = db.weapons
WeaponBuildsList.weaponAttachmentsCollection = db.weaponAttachments
WeaponBuildsList.usersCollection = db.users

WeaponBuilds.weaponBuildsCollection = db.weaponBuilds

########### Resources ############
api = Api(app)
api.add_resource(Home, "/", endpoint="home")

# Weapons endpoints
api.add_resource(WeaponsList, "/weapons")
api.add_resource(Weapons, "/weapons/<string:id>")

api.add_resource(WeaponTypesList, "/weaponTypes")
api.add_resource(WeaponTypes, "/weaponTypes/<string:id>")

api.add_resource(WeaponAttachmentTypesList, "/weaponAttachmentTypes")
api.add_resource(WeaponAttachmentTypes, "/weaponAttachmentTypes/<string:id>")

api.add_resource(WeaponAttachmentsList, "/weaponAttachments")
api.add_resource(WeaponAttachments, "/weaponAttachments/<string:id>")

# Weapon builds endpoints 
api.add_resource(WeaponBuildsList, "/builds")
api.add_resource(WeaponBuilds, "/builds/<string:id>")

# User endpoints
api.add_resource(UsersRegister, "/register")

api.add_resource(UsersLogin, "/login")
api.add_resource(TokenRefresh, "/token/refresh")
api.add_resource(UsersProfile, "/user/profile")

api.add_resource(UsersList, "/users")

# Secret resources
api.add_resource(SecretResource, "/secret")

# Nightbots 
api.add_resource(NightbotRegister, "/nightbot/register/<string:userId>")
api.add_resource(NightbotUnregister, "/nightbot/unregister")

# api.add_resource(WeaponAttachments, "/weapon/attachments/weapon/<string:weaponName>", endpoint="weaponattachmentsweaponname")
# api.add_resource(WeaponAttachments, "/weapon/attachments/weaponid/<string:weaponId>", endpoint="weaponattachmentsweaponId")

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
  
