from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class WeaponTypesList(Resource):
  
  data = []
  totalPages = 0
  currentPage = 0

  db = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('search', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('page',  type = int, default = 1, location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(WeaponTypesList, self).__init__()

  def get(self):
    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    weaponTypes = [] 
    weaponTypesTotalCount = self.db.weaponTypes.find(query).count()

    if args['limit'] > 0:
      skips = args['limit'] * (args['page'] - 1)
      weaponTypes = self.db.weaponTypes.find(query).skip(skips).limit(args['limit'])
      totalPages = round(weaponTypesTotalCount / args['limit'])
      self.totalPages = totalPages
      self.currentPage = args['page']

      self.data = parse_json(weaponTypes)

      return jsonify(status = "ok", data = self.data, totalPages = self.totalPages, currentPage = self.currentPage, totalElements=weaponTypesTotalCount)

    else:
      weaponTypes = self.db.weaponTypes.find(query)
      self.data = parse_json(weaponTypes)

      return jsonify(status = "ok", data = self.data)

  def post(self): 
    if not request.is_json:
      return {"response" : "Incorrect json"}, 500
    
    requestJson = request.get_json()

    if not requestJson: 
      return {}, 201
    
    # Check if name lower field has been send
    if not hasattr(requestJson, "name_lower"):
      requestJson['name_lower'] = requestJson['name'].lower().strip().replace(" ", "")

    # Check if weapon type already exists
    weaponTypeExists = self._checkIfExists(requestJson['name_lower'])
    if weaponTypeExists: 
      return {"response" : "Weapon type {} already exists!".format(requestJson['name'])}, 201
        
    weaponType = parse_json(requestJson)
        
    weaponTypeAdd = self.db.weaponTypes.insert_one(weaponType)
    weaponTypeAddId = weaponTypeAdd.inserted_id

    # Find added weapon type in db
    weaponTypeGet = self.db.weaponTypes.find_one({"_id" : ObjectId(weaponTypeAddId)})
    self.data = parse_json(weaponTypeGet)

    return jsonify(status = "ok", data = self.data)

  def _checkIfExists(self, name_lower):
    exists = False

    weaponType = self.db.weaponTypes.find_one({"name_lower" : name_lower})

    # Weapon attachemnt exists
    if weaponType:
      exists = True

    return exists

class WeaponTypes(Resource): 
  
  data = []
  db = None

  def __init__(self):

    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(WeaponTypes, self).__init__()

  # Get weapon type by id
  def get(self, id):
    weaponTypes = self.db.weaponTypes.find_one({"_id" : ObjectId(id)})
    weaponTypes = parse_json(weaponTypes)

    self.data = weaponTypes    

    return jsonify(status = "ok", data = self.data)
  
  # Update weapon type
  def put(self, id):

    if not request.is_json:
      return {"response" : "Incorrect json"}, 500

    requestJson = request.get_json()

    if not requestJson: 
      return {"response" : "Incorrect json"}, 500

    # Get fields to be updated
    updateFields = self._getUpdateFileds(requestJson)
    if not updateFields: 
      return {}, 204 # nothing to do
      
    update = {}
    update['$set'] = updateFields

    # Update
    updateResult = self.db.weaponTypes.update_one({"_id": ObjectId(id)}, update)
    if updateResult.matched_count == 0:
      return {"response" : "Weapon type with id {} does not exist!".format(id)}, 404

    # Get updated weapon
    weapon = self.db.weaponTypes.find_one({"_id" : ObjectId(id)})

    # Set data
    self.data = parse_json(weapon)

    return jsonify(status = "ok", data = self.data)

  # Remove weapon type by id
  def delete(self, id):
    weaponTypeDelete = self.db.weaponTypes.find_one_and_delete({"_id" : ObjectId(id)})
    weaponTypeDelete = parse_json(weaponTypeDelete)

    if not weaponTypeDelete:
      return {"response" : "Weapon type with {} does not exist!".format(id)}, 404
    
    return {"response" : "Weapon type {} successfully deleted!".format(weaponTypeDelete['name'])}, 204

  def _getUpdateFileds(self, requestJson):
    updateFields = {}

    # Check name field update
    if 'name' in requestJson.keys():
      requestJson['name_lower'] = requestJson['name'].lower().strip().replace(" ", "")

      updateFields['name'] = requestJson['name']
      updateFields['name_lower'] = requestJson['name_lower']

    return updateFields
    