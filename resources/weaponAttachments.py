from flask import request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class WeaponAttachmentsList(Resource):

  data = [] 
  weaponsCollection = None
  weaponAttachmentsCollection = None
  weaponAttachmentTypesCollection = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('weapon', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('weapon_id', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('type', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('type_id', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    super(WeaponAttachmentsList, self).__init__()

  def get(self):
    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    if 'weapon' in query.keys(): 
      weapon = self.weaponsCollection.find_one({"name_lower" : query['weapon']})

      if weapon: 
        weapon = parse_json(weapon)
        query['weapon_id'] = ObjectId(weapon['_id'])
        query.pop('weapon')

    if 'type' in query.keys(): 
      weaponAttachmentType = self.weaponAttachmentTypesCollection.find_one({"name_lower" : query['type']})

      if weaponAttachmentType:
        weaponAttachmentType = parse_json(weaponAttachmentType)
        query['type_id'] = ObjectId(weaponAttachmentType['_id'])
        query.pop('type')

    weaponAttachments = [] 
    if args['limit'] > 0:
      weaponAttachments = self.weaponAttachmentsCollection.find(query).limit(args['limit'])
    else:
      weaponAttachments = self.weaponAttachmentsCollection.find(query)
    
    self.data = parse_json(weaponAttachments)

    return jsonify(status = "ok", data = self.data)

  def post(self):
    # Check if json body is passed
    if not request.is_json:
      return {"response" : "Incorrect json"}, 500
    
    # Set data 
    self.data = request.get_json()

    # Check data
    if not self.data:
      return {"response" : "Incorrect json"}, 500

    # Set name_lower if not set
    if not hasattr(self.data, "name_lower"):
      self.data['name_lower'] = self.data['name'].lower().strip().replace(" ", "")

    # Check if the attachment type already exists
    weaponAttachmentExists = self._checkIfExists(self.data['name_lower'], self.data['weapon_id'])
    if weaponAttachmentExists:

      # Get weapon to display name in the error message
      weapon = self.weaponsCollection.find_one({"_id" : ObjectId(self.data['weapon_id'])})
      weapon = parse_json(weapon)

      return {"response" : "Weapon attachment {} already exists for weapon {} !".format(self.data['name'], weapon['name'])}, 201

    # TODO validate fields
    self.data['type_id'] = ObjectId(self.data['type_id'])
    self.data['weapon_id'] = ObjectId(self.data['weapon_id'])

    weaponAttachmentAdd = self.weaponAttachmentsCollection.insert_one(self.data)
    weaponAttachmentAddId = weaponAttachmentAdd.inserted_id

    # Find added weapon attachment type in db
    weaponAttachmentGet = self.weaponAttachmentsCollection.find_one({"_id" : ObjectId(weaponAttachmentAddId)})

    # Set data
    self.data = parse_json(weaponAttachmentGet)

    return jsonify(status = "ok", data = self.data)

  def _checkIfExists(self, name_lower, weaponId):
    exists = False

    weaponAttachment = self.weaponAttachmentsCollection.find({"name_lower" : name_lower, "weapon_id" : ObjectId(weaponId)})

    # Weapon attachemnt exists
    if weaponAttachment:
      exists = True

    return exists
    
class WeaponAttachments(Resource):

  data = []
  weaponsCollection = None
  weaponAttachmentsCollection = None

  def get(self, id):
    weaponAttachment = self.weaponAttachmentsCollection.find_one({"_id" : ObjectId(id)})
    if not weaponAttachment:
      return {"response" : "Weapon attachment with {} does not exist!".format(id)}, 404
    
    weaponAttachment = parse_json(weaponAttachment)

    self.data = parse_json(weaponAttachment)

    return jsonify(status = "ok", data = self.data)
  
  def delete(self, id):
    weaponAttachment = self.weaponAttachmentsCollection.find_one_and_delete({"_id" : ObjectId(id)})
    if not weaponAttachment:
      return {"response" : "Weapon attachment with {} does not exist!".format(id)}, 404

    weaponAttachment = parse_json(weaponAttachment)

    return {"response" : "Weapon attachment {} successfully deleted!".format(weaponAttachment['name'])}, 204