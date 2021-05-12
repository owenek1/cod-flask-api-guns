from flask import request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class WeaponBuildsList(Resource):

  data = []

  weaponBuildsCollection = None
  weaponsCollection = None
  weaponAttachmentsCollection = None
  usersCollection = None

  def __init__(self):
      self.reqparseGet = reqparse.RequestParser()
      self.reqparseGet.add_argument('weapon', type = str, default = "", location = 'args')
      self.reqparseGet.add_argument('weapon_id', type = str, default = "", location = 'args')
      self.reqparseGet.add_argument('user', type = str, default = "", location = 'args')
      self.reqparseGet.add_argument('user_id', type = str, default = "", location = 'args')
      self.reqparseGet.add_argument('nightbot', type=bool, default = False, location='args')
      self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

      self.reqparsePost = reqparse.RequestParser()
      self.reqparsePost.add_argument('name', type = str, required = True, location = 'json')
      self.reqparsePost.add_argument('user_id', type = str, required = True, location = 'json')
      self.reqparsePost.add_argument('weapon_id', type = str, required = True, location = 'json')

      super(WeaponBuildsList, self).__init__()

  def get(self): 
    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    print(args['nightbot'])
    
    # Filter by weapon
    if 'weapon' in query.keys():
      weapon = self.weaponsCollection.find_one({"name_lower" : {"$regex": query['weapon']}})
      weapon = parse_json(weapon)

      # Return empty list if weapon not found
      if not weapon:
        return jsonify(status = "ok", data = self.data)

      weaponId = ObjectId(weapon['_id'])
      query['weapon_id'] = weaponId
      query.pop('weapon')

    # Filter by user
    if 'user' in query.keys():
      user = self.usersCollection.find_one({"email" : {"$regex": query['user']}})
      user = parse_json(user)

      # Return empty list if user not found
      if not user:
        return jsonify(status = "ok", data = self.data)

      userId = ObjectId(user['_id'])
      query['user_id'] = userId

      query.pop('user')

    weaponBuilds = [] 
    if args['limit'] > 0:
      weaponBuilds = self.weaponBuildsCollection.find(query).limit(args['limit'])
    else:
      weaponBuilds = self.weaponBuildsCollection.find(query)

    # Format output for night bot
    if args['nightbot']: 

      nightBotResponse = []

      for build in weaponBuilds: 

        buildToAdd = {}

        buildToAdd['name'] = build['name']
        lengthAttachments = len(build['attachments'])
        buildToAdd['nr_of_attachments'] = lengthAttachments

        if lengthAttachments > 0: 
          
          attachmentIterator = 1
          for attachmentId in build['attachments']:

            attachment = self.weaponAttachmentsCollection.find_one({"_id" : ObjectId(attachmentId)})
            attachment = parse_json(attachment)

            buildToAdd['attachment_' + str(attachmentIterator)] = attachment['name']

            attachmentIterator += 1 

        nightBotResponse.append(buildToAdd)

      self.data = parse_json(nightBotResponse)
      
    else:

      self.data = parse_json(weaponBuilds)

    return jsonify(status = "ok", data = self.data)

  def post(self):
    if not request.is_json:
      return {"response" : "Incorrect json"}, 500
    
    requestJson = request.get_json()

    if not requestJson: 
      return {"response" : "Incorrect json"}, 500
    
    # Check if name lower field has been send
    if not hasattr(requestJson, "name_lower"):
      requestJson['name_lower'] = requestJson['name'].lower().strip().replace(" ", "")

    # Check if user exits
    user = self.usersCollection.find_one({"_id" : ObjectId(requestJson['user_id'])})
    if not user: 
      return {}, 204 # nothing todo 
    
    requestJson['user_id'] = ObjectId(requestJson['user_id'])

    # Check if weapon exists
    weapon = self.weaponsCollection.find_one({"_id" : ObjectId(requestJson['weapon_id'])})
    if not weapon: 
      return {}, 204 # nothing todo
    
    requestJson['weapon_id'] = ObjectId(requestJson['weapon_id'])
      
    # Check if weapon attachments exist
    weaponAttachments = requestJson['attachments']
    weaponAttachmentsAmount = len(weaponAttachments)

    inQuery = []
    for weaponAt in weaponAttachments: 
      inQuery.append(ObjectId(weaponAt))

    # Find all weapon attachments to check if they exist
    attachments = self.weaponAttachmentsCollection.find({ "_id": { "$in": inQuery } })
    attachments = parse_json(attachments)
    attachmentsFound = len(attachments)

    if weaponAttachmentsAmount != attachmentsFound: 
      return {}, 204
    
    requestJson['attachments'] = inQuery

    weaponBuildAdd = self.weaponBuildsCollection.insert_one(requestJson)
    weaponBuildAddedId = weaponBuildAdd.inserted_id

    weaponBuild = self.weaponBuildsCollection.find_one({"_id" : ObjectId(weaponBuildAddedId)})
    
    self.data = parse_json(weaponBuild)
    
    return jsonify(status = "ok", data = self.data)

class WeaponBuilds(Resource): 

  data = []
  weaponBuildsCollection = None

  def get(self, id): 
    weaponBuild = self.weaponBuildsCollection.find_one({"_id" : ObjectId(id)})
    self.data = parse_json(weaponBuild)

    return jsonify(status = "ok", data = self.data)