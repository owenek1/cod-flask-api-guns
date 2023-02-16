from flask import current_app, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json, validate_objectId

from bson.objectid import ObjectId

from models.weapons import Weapons

class WeaponAttachmentsList(Resource):

  db = None

  # Pagination parameters
  totalPages = 0
  currentPage = 1
  totalElements = 0

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('weapon', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('weapon_id', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('type', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('type_id', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('search', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('page',  type = int, default = 1, location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('name', type = str, required=True, location = 'json')
    self.reqparsePost.add_argument('weapon_id', type = str, required=True, location = 'json')
    self.reqparsePost.add_argument('type_id', type = str, required=True, location = 'json')

    super(WeaponAttachmentsList, self).__init__()

  def get(self):

    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Check if weapon_id is type ObjectId
    validate_objectId(args, 'weapon_id')

    # Check if type_id is type ObjectId
    validate_objectId(args, 'type_id')
      
    # if weapon and weapon_id in args are not empty make bad request
    if (args['weapon_id'] != "" and args['weapon'] != ""):
      return {}, 400

    # if type and type_id in args are not empty make bad request
    if (args['type_id'] != "" and args['type'] != ""):
      return {}, 400

    # Build query to filter the db results
    query = build_query(args)

    if 'weapon' in query.keys(): 
      weapon = self.db.weapons.find_one({"name_lower" : {"$regex": query['weapon']}})

      if weapon: 
        weapon = parse_json(weapon)
        query['weapon_id'] = ObjectId(weapon['_id'])
        query.pop('weapon')

    if 'type' in query.keys(): 
      weaponAttachmentType = self.db.weaponAttachmentTypes.find_one({"name_lower" : {"$regex": query['type']}})

      if weaponAttachmentType:
        weaponAttachmentType = parse_json(weaponAttachmentType)
        query['type_id'] = ObjectId(weaponAttachmentType['_id'])
        query.pop('type')

    weaponAttachments = []
    totalElements = self.db.weaponAttachmentTypes.find(query).count()

    if args['limit'] > 0:
      skips = args['limit'] * (args['page'] - 1)
      weaponAttachments = self.db.weaponAttachments.find(query).skip(skips).limit(args['limit'])
      totalPages = round(totalElements / args['limit'])
      currentPage = args['page']

      return jsonify(status = "ok", data = parse_json(weaponAttachments), totalPages = totalPages, currentPage = currentPage, totalElements=totalElements)

    else:
      weaponAttachments = self.db.weaponAttachments.find(query)
  
      return jsonify(status = "ok", data = parse_json(weaponAttachments))

  def post(self):
    # Parse arguments
    args = self.reqparsePost.parse_args()

    # Set name lower field
    args['name_lower'] = args['name'].lower().strip().replace(" ", "")

    # Check if weapon_id and type_id are type ObjectId
    if not ObjectId.is_valid(args['weapon_id']) or not ObjectId.is_valid(args['type_id']):
      return {}, 400

    # Set ObjectId
    args['type_id'] = ObjectId(self.data['type_id'])
    args['weapon_id'] = ObjectId(self.data['weapon_id'])

    # Check if the attachment type already exists
    weaponAttachmentExists = self._checkIfExists(args['name_lower'], args['weapon_id'])
    if weaponAttachmentExists:

      # Get weapon to display name in the error message
      weapon = self.db.weapons.find_one({"_id" : ObjectId(args['weapon_id'])})
      weapon = parse_json(weapon)

      return {"response" : "Weapon attachment {} already exists for weapon {} !".format(args['name'], weapon['name'])}, 201

    weaponAttachmentAdd = self.db.weaponAttachments.insert_one()
    weaponAttachmentAddId = weaponAttachmentAdd.inserted_id

    # Find added weapon attachment in db
    weaponAttachmentGet = self.db.weaponAttachments.find_one({"_id" : ObjectId(weaponAttachmentAddId)})

    return jsonify(status = "ok", data = parse_json(weaponAttachmentGet))

  def _checkIfExists(self, name_lower, weaponId):
    exists = False

    weaponAttachment = self.db.weaponAttachments.find({"name_lower" : name_lower, "weapon_id" : ObjectId(weaponId)})
    weaponAttachment = parse_json(weaponAttachment)
    
    # Weapon attachemnt exists
    if weaponAttachment:
      exists = True

    return exists
    
class WeaponAttachments(Resource):

  db = None

  def __init__(self):

    super(WeaponAttachments, self).__init__()

  def get(self, id):
    
    # Validate Id 
    if not ObjectId.is_valid(id):
      return {}, 400 # bad request, id is not a valid ObjectId

    # Get weapon attachment
    weaponAttachment = self.db.weaponAttachments.find_one({"_id" : ObjectId(id)})

    if weaponAttachment is None:
      return {}, 404 # return not found
    
    return jsonify(status = "ok", data = parse_json(weaponAttachment))
  
  def delete(self, id):

    # Validate Id 
    if not ObjectId.is_valid(id):
      return {}, 400 # bad request, id is not a valid ObjectId

    weaponAttachment = self.weaponAttachmentsCollection.find_one_and_delete({"_id" : ObjectId(id)})
    
    if weaponAttachment is None:
      return {}, 404 # return not found

    return {}, 204