from flask import request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class WeaponTypesList(Resource):
  
  data = []
  weaponTypesCollection = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    super(WeaponTypesList, self).__init__()

  def get(self):
    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    weaponTypes = [] 
    if args['limit'] > 0:
      weaponTypes = self.weaponTypesCollection.find(query).limit(args['limit'])
    else:
      weaponTypes = self.weaponTypesCollection.find(query)
    
    self.data = parse_json(weaponTypes)

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

    # Check if weapon type already exists
    weaponTypeExists = self._checkIfExists(requestJson['name_lower'])
    if weaponTypeExists: 
      return {"response" : "Weapon type {} already exists!".format(requestJson['name'])}, 201
        
    weaponType = parse_json(requestJson)
        
    weaponTypeAdd = self.weaponTypesCollection.insert_one(weaponType)
    weaponTypeAddId = weaponTypeAdd.inserted_id

    # Find added weapon type in db
    weaponTypeGet = self.weaponTypesCollection.find_one({"_id" : ObjectId(weaponTypeAddId)})
    self.data = parse_json(weaponTypeGet)

    return jsonify(status = "ok", data = self.data)

  def _checkIfExists(self, name_lower):
    exists = False

    weaponType = self.weaponTypesCollection.find_one({"name_lower" : name_lower})

    # Weapon attachemnt exists
    if weaponType:
      exists = True

    return exists

class WeaponTypes(Resource): 
  
  data = []
  weaponTypesCollection = None
  
  # Get weapon by id
  def get(self, id):
    weaponTypes = self.weaponTypesCollection.find_one({"_id" : ObjectId(id)})
    weaponTypes = parse_json(weaponTypes)

    self.data = weaponTypes    

    return jsonify(status = "ok", data = self.data)
  
  def delete(self, id):
    weaponTypeDelete = self.weaponTypesCollection.find_one_and_delete({"_id" : ObjectId(id)})
    weaponTypeDelete = parse_json(weaponTypeDelete)

    if not weaponTypeDelete:
      return {"response" : "Weapon type with {} does not exist!".format(id)}, 404
    
    return {"response" : "Weapon type {} successfully deleted!".format(weaponTypeDelete['name'])}, 204
    