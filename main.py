from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_pymongo import PyMongo

from bson.objectid import ObjectId

from utils import parse_json, build_query

# Resources
from resources.weapons import Weapons, WeaponsList
from resources.weaponTypes import WeaponTypes, WeaponTypesList
from resources.weaponAttachmentTypes import WeaponAttachmentTypes, WeaponAttachmentTypesList
from resources.weaponAttachments import WeaponAttachments, WeaponAttachmentsList
from resources.twitchStreamers import TwitchStreamers, TwitchStreamersList
from resources.weaponBuilds import WeaponBuilds, WeaponBuildsList

# Flask app configuration
app = Flask(__name__)

# Mongo DB
mongo_db_uri = "mongodb+srv://admin:owenek@cluster0.ur0zv.mongodb.net/restAPIWeapons?retryWrites=true&w=majority"
mongo = PyMongo(app, uri=mongo_db_uri)
db = mongo.db

# TODO
# app.config['dbCollections'] = {
#   "weapons" : db.weapons,
#   "weaponTypes" : db.weaponTypes,
#   "weaponAttachments" : db.weaponAttachments,
#   "weaponAttachmentTypes" : db.weaponAttachmentTypes,
#   "streamers" : db.twitchStreamers,
#   "weponBuilds" : db.weaponBuilds
# }

# DB collections for resources
Weapons.weaponsCollection = db.weapons
Weapons.weaponTypesCollection = db.weaponTypes

WeaponsList.weaponsCollection = db.weapons
WeaponsList.weaponTypesCollection = db.weaponTypes

WeaponTypes.weaponTypesCollection = db.weaponTypes
WeaponTypesList.weaponTypesCollection = db.weaponTypes

WeaponAttachmentTypes.weaponAttachmentTypesCollection = db.weaponAttachmentTypes
WeaponAttachmentTypesList.weaponAttachmentTypesCollection = db.weaponAttachmentTypes

WeaponAttachments.weaponAttachmentsCollection = db.weaponAttachments
WeaponAttachments.weaponsCollection = db.weapons

WeaponAttachmentsList.weaponAttachmentsCollection = db.weaponAttachments
WeaponAttachmentsList.weaponsCollection = db.weapons
WeaponAttachmentsList.weaponAttachmentTypesCollection = db.weaponAttachmentTypes

TwitchStreamersList.streamersCollection = db.twitchStreamers
TwitchStreamers.streamersCollection = db.twitchStreamers

WeaponBuildsList.weaponBuildsCollection = db.weaponBuilds
WeaponBuildsList.streamersCollection = db.twitchStreamers
WeaponBuildsList.weaponsCollection = db.weapons
WeaponBuildsList.weaponAttachmentsCollection = db.weaponAttachments

WeaponBuilds.weaponBuildsCollection = db.weaponBuilds

######### Resources #########
class Home(Resource): 
  def get(self):
    return jsonify(api = "Rest API Call of Duty Warzone", version = "v1.0", author="Owen", email="owenek123@gmail.com")

########### API ############
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

api.add_resource(TwitchStreamersList, "/streamers")
api.add_resource(TwitchStreamers, "/streamers/<string:id>")

api.add_resource(WeaponBuildsList, "/builds")
api.add_resource(WeaponBuilds, "/builds/<string:id>")

# api.add_resource(WeaponAttachments, "/weapon/attachments/weapon/<string:weaponName>", endpoint="weaponattachmentsweaponname")
# api.add_resource(WeaponAttachments, "/weapon/attachments/weaponid/<string:weaponId>", endpoint="weaponattachmentsweaponId")

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
  
