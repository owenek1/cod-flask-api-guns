from flask import request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId


class NightBotsList(Resource):

  data = []
  nightbotsCollection = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('twitch_username', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('twitch_profile', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    # self.reqparsePost = reqparse.RequestParser()
    # self.reqparsePost.add_argument('name', type=str, required=True, location='json')
    # self.reqparsePost.add_argument('twitch_username', type=str, required=True, location='json')
    # self.reqparsePost.add_argument('twitch_profile',  type=str, required=True, location='json')

    super(NightBotsList, self).__init__()

  # Get all nightbots 
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