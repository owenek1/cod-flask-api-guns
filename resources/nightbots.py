from flask import current_app, request
from flask_restful import Resource

from bson.objectid import ObjectId

from datetime import datetime

from utils import parse_json

class NightbotRegister(Resource):

  db = None 

  def __init__(self): 
    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']
    super(NightbotRegister, self).__init__()

  def get(self, userId):
    requestHeaders = request.headers

    # Process nightbot information
    # Example of Nightbot-Channel header
    # Nightbot-Channel: name=night&displayName=Night&provider=twitch&providerId=11785491
    if not "Nightbot-Channel" in requestHeaders.keys(): 
      return {"message": "Invalid request"}, 400
    
    nightbotChannelHeader = requestHeaders['Nightbot-Channel']
    nightbotInfo = nightbotChannelHeader.split("&")
    nightbotInfoList = {
      "name": "",
      "displayName" : "",
      "provider" : "",
      "providerId" : 0
    }

    for info in nightbotInfo:
      infoSplit = info.split("=")

      field = infoSplit[0]
      value = infoSplit[1]

      nightbotInfoList[field] = value

    # Check if user with that id is registered and can register a nightbot
    user = self.db.users.find_one({"_id" : ObjectId(userId)})
    user = parse_json(user)

    if len(user) == 0: 
      return {"message" : "User not found!"}, 201
    
    # Check if nighbot already registered for the user
    nightbotCheck = self.db.nightbots.find_one({"user_id" : ObjectId(userId)})
    nightbotCheck = parse_json(nightbotCheck)

    if nightbotCheck is not None and len(nightbotCheck) > 0: 
      # Nightbot already registered for this user
      return {"message" : "Nightbot already registered!"}, 201
    
    data = {}

    # Register nightbot for the user
    data['user_id'] = ObjectId(userId)
    data['registered_on'] = datetime.now()
    data['provider'] = nightbotInfoList['provider']
    data['provider_id'] = nightbotInfoList['providerId']

    nightbotRegister = self.nightbotsCollection.insert_one(data)
    nightbotRegisterId = nightbotRegister.inserted_id

    nightbot = self.nightbotsCollection.find_one({"_id" : ObjectId(nightbotRegisterId)})
    
    if nightbot is None: 
      return {"message" : "Nightbot not registered!"}, 400

    return {"message" : "Nightbot registered successfully!"}, 200

class NightbotUnregister(Resource): 
  db = None 

  def __init__(self): 
    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']
    super(NightbotUnregister, self).__init__()

  def get(self):

    requestHeaders = request.headers

    # Process nightbot information
    # Example of Nightbot-Channel header
    # Nightbot-Channel: name=night&displayName=Night&provider=twitch&providerId=11785491
    if not "Nightbot-Channel" in requestHeaders.keys(): 
      return {"message": "Invalid request"}, 400
    
    nightbotChannelHeader = requestHeaders['Nightbot-Channel']
    nightbotInfo = nightbotChannelHeader.split("&")
    nightbotInfoList = {
      "name": "",
      "displayName" : "",
      "provider" : "",
      "providerId" : 0
    }

    for info in nightbotInfo:
      infoSplit = info.split("=")

      field = infoSplit[0]
      value = infoSplit[1]

      nightbotInfoList[field] = value

    # Check if nighbot registered
    self.db.nightbots.find_one_and_delete({"provider_id" : nightbotInfoList['providerId']})

    return {"message" : "Nightbot unregistered successfully!"}, 200
