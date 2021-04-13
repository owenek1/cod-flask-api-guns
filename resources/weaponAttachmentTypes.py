from flask import request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class WeaponAttachmentTypes(Resource):
  data = []
  weaponAttachmentTypesCollection = None

  def get(self, id):
    weaponAttachmentType = self.weaponAttachmentTypesCollection.find_one({"_id" : ObjectId(id)})
    weaponAttachmentType = parse_json(weaponAttachmentType)

    if not weaponAttachmentType:
      return {"response" : "Weapon attachment type with {} does not exist!".format(id)}, 404

    self.data = weaponAttachmentType

    return jsonify(status = "ok", data = self.data)
  
  def delete(self, id):
    weaponAttachmentType = self.weaponAttachmentTypesCollection.find_one_and_delete({"_id" : ObjectId(id)})
    weaponAttachmentType = parse_json(weaponAttachmentType)

    if not weaponAttachmentType:
      return {"response" : "Weapon attachment type with {} does not exist!".format(id)}, 404

    return {"response" : "Weapon attachment type {} successfully deleted!".format(weaponAttachmentType['name'])}, 204

class WeaponAttachmentTypesList(Resource):
  data = []
  weaponAttachmentTypesCollection = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    super(WeaponAttachmentTypesList, self).__init__()
  
  def get(self):

    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    weaponAttachmentTypes = [] 
    if args['limit'] > 0:
      weaponAttachmentTypes = self.weaponAttachmentTypesCollection.find(query).limit(args['limit'])
    else:
      weaponAttachmentTypes = self.weaponAttachmentTypesCollection.find(query)
    
    self.data = parse_json(weaponAttachmentTypes)

    return jsonify(status = "ok", data = self.data)

  def post(self):
    # Check if json body is used
    if not request.is_json:
      return {"response" : "Incorrect json"}, 500

    self.data = request.get_json()

    if not self.data:
      return {"response" : "Incorrect json"}, 500

    # Check if name lower field has been send
    if not hasattr(self.data, "name_lower"):
      self.data['name_lower'] = self.data['name'].lower().strip().replace(" ", "")

    # Check if the attachment type already exists
    weaponAttachmentTypeExists = self._checkWeaponAttachmentTypeExists(self.data['name_lower'])
    if weaponAttachmentTypeExists:
        return {"response" : "Weapon attachment type with name {} already exists!".format(self.data['name'])}, 201

    weaponAttachmentTypeAdd = self.weaponAttachmentTypesCollection.insert_one(self.data)
    weaponAttachmentTypeAddId = weaponAttachmentTypeAdd.inserted_id

    # Find added weapon attachment type in db
    weaponAttachmentTypeGet = self.weaponAttachmentTypesCollection.find_one({"_id" : ObjectId(weaponAttachmentTypeAddId)})

    self.data = parse_json(weaponAttachmentTypeGet)

    return jsonify(status = "ok", data = self.data)
  
  def _checkWeaponAttachmentTypeExists(self, name_lower):
    exists = False

    weaponAttachmentType = self.weaponAttachmentTypesCollection.find({"name_lower" : name_lower})

    # Weapon attachemnt exists
    if weaponAttachmentType:
      exists = True

    return exists