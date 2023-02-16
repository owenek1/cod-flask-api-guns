from flask import current_app, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

class WeaponAttachmentTypes(Resource):

  db = None

  def __init__(self):
    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(WeaponAttachmentTypes, self).__init__()

  def get(self, id):

    # Validate Id 
    if not ObjectId.is_valid(id):
      return {}, 400 # bad request, id is not a valid ObjectId

    weaponAttachmentType = self.db.weaponAttachmentTypes.find_one({"_id" : ObjectId(id)})

    if weaponAttachmentType is None:
      return {}, 404 # return not found
    
    return jsonify(status = "ok", data = parse_json(weaponAttachmentType))
  
  def delete(self, id):
    
    # Validate Id 
    if not ObjectId.is_valid(id):
      return {}, 400 # bad request, id is not a valid ObjectId

    weaponAttachmentType = self.db.weaponAttachmentTypes.find_one_and_delete({"_id" : ObjectId(id)})

    if weaponAttachmentType is None:
      return {}, 404 # return not found

    return {}, 204

class WeaponAttachmentTypesList(Resource):

  db = None

  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('search', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('page',  type = int, default = 1, location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('name', type=str, required=True, location = 'json')

    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(WeaponAttachmentTypesList, self).__init__()
  
  def get(self):

    # Pagination parameters
    totalPages = 0
    currentPage = 1
    totalElements = 0

    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    weaponAttachmentTypes = [] 
    totalElements = self.db.weaponAttachmentTypes.find(query).count()

    if args['limit'] > 0:
      skips = args['limit'] * (args['page'] - 1)
      weaponAttachmentTypes = self.db.weaponAttachmentTypes.find(query).skip(skips).limit(args['limit'])
      totalPages = round(totalElements / args['limit'])
      totalPages = totalPages
      currentPage = args['page']

      return jsonify(status = "ok", data = parse_json(weaponAttachmentTypes), totalPages = totalPages, currentPage = currentPage, totalElements=totalElements)

    else:
      weaponAttachmentTypes = self.db.weaponAttachmentTypes.find(query)
      return jsonify(status = "ok", data = parse_json(weaponAttachmentTypes))
  
  def post(self):
    # Parse arguments
    args = self.reqparsePost.parse_args()

    # Set name lower field
    args['name_lower'] = args['name'].lower().strip().replace(" ", "")

    # Weapon attachment type add
    weaponAttachmentTypeAdd = self.db.weaponAttachmentTypes.insert_one(args)
    weaponAttachmentTypeAddId = weaponAttachmentTypeAdd.inserted_id

    # Find added weapon attachment type in db
    weaponAttachmentTypeGet = self.db.weaponAttachmentTypes.find_one({"_id" : ObjectId(weaponAttachmentTypeAddId)})

    return jsonify(status = "ok", data = parse_json(weaponAttachmentTypeGet))