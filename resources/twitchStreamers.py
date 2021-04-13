from flask import request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class TwitchStreamersList(Resource):

  data = []
  streamersCollection = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('twitch_username', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('twitch_profile', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('name', type=str, required=True, location='json')
    self.reqparsePost.add_argument('twitch_username', type=str, required=True, location='json')
    self.reqparsePost.add_argument('twitch_profile',  type=str, required=True, location='json')

    super(TwitchStreamersList, self).__init__()

  # Get all streamers
  def get(self):

    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    twitchStreamers = [] 
    if args['limit'] > 0:
      twitchStreamers = self.streamersCollection.find(query).limit(args['limit'])
    else:
      twitchStreamers = self.streamersCollection.find(query)
    
    self.data = parse_json(twitchStreamers)

    return jsonify(status = "ok", data = self.data)

  def post(self):
    # Check if body json is passed
    if not request.is_json:
      return {"response" : "Incorrect json"}, 500

    args = self.reqparsePost.parse_args()

    # Get json data
    requestJson = request.get_json()

    # Check if name lower field has been send
    if not hasattr(args, "name_lower"):
      requestJson['name_lower'] = args['name'].lower().strip().replace(" ", "")

    # Check if the streamer already exists
    streamerExists = self._checkStreamerExists(requestJson['twitch_username'])
    if streamerExists: 
      return {"response" : "Twitch streamer with username {} already exists!".format(requestJson['twitch_username'])}, 204

    streamerAdd = self.streamersCollection.insert_one(requestJson)
    streamerAddId = streamerAdd.inserted_id

    # Find added streamer in db
    streamerGet = self.streamersCollection.find_one({"_id" : ObjectId(streamerAddId)})

    self.data = parse_json(streamerGet)

    return jsonify(status = "ok", data = self.data)

  def _checkStreamerExists(self, username):
    exists = False 

    streamer = self.streamersCollection.find_one({"twitch_username" : username})

    if streamer:
      exists = True
    
    return exists

class TwitchStreamers(Resource):

  data = []
  streamersCollection = None

  def get(self, id): 
    twitchStreamer = self.streamersCollection.find_one({"_id" : ObjectId(id)})
    if not twitchStreamer:
      return {"response" : "Twitch streamer with id {} does not exist!".format(id)}, 404
    
    twitchStreamer = parse_json(twitchStreamer)

    self.data = parse_json(twitchStreamer)

    return jsonify(status = "ok", data = self.data)

  def put(self, id):
    if not request.is_json:
      return {"response" : "Incorrect json"}, 500

    requestJson = request.get_json()

    if not requestJson: 
      return {"response" : "Incorrect json"}, 500

    # Get fields to be updated
    updateFields = self._getUpdateFields(requestJson)
    if not updateFields:
      return {}, 204 # nothing to do

    update = {}
    update['$set'] = updateFields

    # Update
    updateResult = self.streamersCollection.update_one({"_id": ObjectId(id)}, update)
    if updateResult.matched_count == 0:
      return {"response" : "Twitch streamer with id {} does not exist!".format(id)}, 404

    # Get updated weapon
    twitchStreamer = self.streamersCollection.find_one({"_id" : ObjectId(id)})
    
    self.data = parse_json(twitchStreamer)

    return jsonify(status = "ok", data = self.data)

  def _getUpdateFields(self, requestJson):
    updateFields = {}

    # Check name field update
    if 'name' in requestJson.keys():
      requestJson['name_lower'] = requestJson['name'].lower().strip().replace(" ", "")

      updateFields['name'] = requestJson['name']
      updateFields['name_lower'] = requestJson['name_lower']
    
    # Check name twitch username 
    if 'twitch_username' in requestJson.keys():
      updateFields['twitch_username'] = requestJson['twitch_username']
    
    # Check twitch profile
    if 'twitch_profile' in requestJson.keys():
      updateFields['twitch_profile'] = requestJson['twtich_profile']

    return updateFields

  def delete(self, id):
    twitchStreamer = self.streamersCollection.find_one_and_delete({"_id" : ObjectId(id)})
    if not twitchStreamer:
      return {"response" : "Twitch streamer with id {} does not exist!".format(id)}, 404

    twitchStreamer = parse_json(twitchStreamer)

    return {"response" : "Twitch streamer {} successfully deleted!".format(twitchStreamer['twitch_username'])}, 204