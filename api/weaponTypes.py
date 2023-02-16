from flask import jsonify, make_response
from flask_restful import Resource, reqparse

from utils import build_query, parse_json, unset_empty_fields

from bson.objectid import ObjectId

from models.weaponTypes import WeaponTypes as WeaponTypesModel

class WeaponTypesList(Resource):  

  data = [] 
  
  # Pagination parameters
  totalPages = 0
  currentPage = 1
  totalElements = 0
  skip = 0
  
  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('search', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('page',  type = int, default = 1, location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('name', type = str, required=True, location = 'json')
    self.reqparsePost.add_argument('game_ids', type = list, required=True, location = 'json')

    super(WeaponTypesList, self).__init__()

  def get(self):
    
    # Parse arguments
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    # Pagination
    self.totalElements = WeaponTypesModel.objects.count()

    if (args['limit'] > 0):
       self.skip = args['limit'] * (args['page'] - 1)

    # Get weapons
    weaponTypes = WeaponTypesModel.objects(__raw__=query).skip(self.skip).limit(args['limit'])

    # Parse json
    self.data = parse_json(weaponTypes.to_json())

    return jsonify(data=self.data,
                   totalPages=self.totalPages,
                   currentPage=self.currentPage,
                   totalElements=self.totalElements)
    
  def post(self):
    
    # Parse arguments
    args = self.reqparsePost.parse_args()
    
    # Set name lower field
    args['name_lower'] = args['name'].lower().strip().replace(" ", "")

    # Check if weapon type already exists
    weaponTypeExists = self._checkIfExists(args['name_lower'])
    if weaponTypeExists: 
      message = ("Weapon type {} already exists".format(args['name']))
      return make_response(jsonify(status="error", message=message), 201)

    # Verify game ids
    if (len(args['game_ids']) > 0):
      for i in range(0, len(args['game_ids'])):
        if not ObjectId.is_valid(args['game_ids'][i]):
          return make_response(jsonify(status="error", message="Invalid object id"), 201)

    # Save weapon type
    weaponType = WeaponTypesModel(**args)
    weaponType = weaponType.save()

    # Create index after insert
    WeaponTypesModel.create_index('name_lower', background=True)
    
    return jsonify(status = "ok", data = parse_json(weaponType.to_json()))

  def _checkIfExists(self, name_lower):
    exists = False

    weaponType = WeaponTypesModel.objects(name_lower=name_lower).count()

    # Weapon attachemnt exists
    if  weaponType > 0:
      exists = True

    return exists

class WeaponTypes(Resource): 
  
  data = []

  def __init__(self):

    self.reqparsePut = reqparse.RequestParser()
    self.reqparsePut.add_argument('name', type = str, required=False, location = 'json')
    self.reqparsePut.add_argument('game_ids', type = list, required=False, location = 'json')
    
    super(WeaponTypes, self).__init__()

  # Get weapon type by id
  def get(self, id: str):
    
    # Validate id if valid
    if not ObjectId.is_valid(id):
      return make_response(jsonify(status="error", message="Id is not valid"), 400)
    
    weaponTypes = WeaponTypesModel.objects(id=id).first_or_404()

    self.data = parse_json(weaponTypes.to_json())

    return jsonify(status = "ok", data = self.data)
  
  # Update weapon type
  def put(self, id: str):

    # Validate id if valid
    if not ObjectId.is_valid(id):
      return make_response(jsonify(status="error", message="Id is not valid"), 400)
      
    # Parse arguments
    args = self.reqparsePut.parse_args()

    # Unset all empty fields
    args = unset_empty_fields(args)
    if (len(args) == 0):
      return make_response(jsonify(status="error", message="Nothing to update"), 400)
      
    # Get weapon type or return 404
    weaponType = WeaponTypesModel.objects(id=id).first_or_404()
    
    # Update weapon type obj
    weaponType.update(**args)

    # Get updated obj
    weaponType = WeaponTypesModel.objects(id=id).first_or_404()

    # Create index after update
    WeaponTypesModel.create_index('name_lower', background=True)
    
    # Set data
    self.data = parse_json(weaponType.to_json())

    return make_response(jsonify(status = "ok", data = self.data), 200)

  # Remove weapon type by id
  def delete(self, id: str):
    
    # Validate id if valid
    if not ObjectId.is_valid(id):
      return make_response(jsonify(status="error", message="Id is not valid"), 400)
      
    count = WeaponTypesModel.objects(id=id).delete()
    
    return make_response(jsonify(status = "ok", count=count), 200)