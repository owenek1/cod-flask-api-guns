from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse

from utils import build_query, parse_json

from bson.objectid import ObjectId

from models.games import Games as GamesModel

class GamesList(Resource):  

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

    super(GamesList, self).__init__()

  def get(self):
    
    # Parse arguments
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    # Pagination
    self.totalElements = GamesModel.objects.count()

    if (args['limit'] > 0):
       self.skip = args['limit'] * (args['page'] - 1)

    # Get weapons
    weaponTypes = GamesModel.objects(__raw__=query).skip(self.skip).limit(args['limit'])

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
      return {"response" : "Weapon type {} already exists!".format(args['name'])}, 201

    # Save weapon type
    weaponType = GamesModel(**args)
    weaponType = weaponType.save()

    # Create index after insert
    GamesModel.create_index('name_lower', background=True)
    
    return jsonify(status = "ok", data = parse_json(weaponType.to_json()))

  def _checkIfExists(self, name_lower):
    exists = False

    weaponType = GamesModel.objects(name_lower=name_lower)

    # Weapon attachemnt exists
    if weaponType:
      exists = True

    return exists

class Games(Resource): 
  
  data = []

  def __init__(self):

    self.reqparsePut = reqparse.RequestParser()
    self.reqparsePut.add_argument('name', type = str, required=True, location = 'json')
    
    super(WeaponTypes, self).__init__()

  # Get weapon type by id
  def get(self, id: str):
    
    # Validate id if valid
    if not ObjectId.is_valid(id):
      return {}, 400 # bad request, id is not a valid ObjectId
    
    weaponTypes = GamesModel.objects(id=id).first_or_404()

    self.data = parse_json(weaponTypes.to_json())

    return jsonify(status = "ok", data = self.data)
  
  # Update weapon type
  def put(self, id):
    
    # Parse arguments
    args = self.reqparsePut.parse_args()
    
    # Set name lower field
    args['name_lower'] = args['name'].lower().strip().replace(" ", "")
    
    # Get weapon type or return 404
    game = GamesModel.objects(id=id).first_or_404()

    # Update weapon type obj
    game.update(**args)

    # Get updated obj
    game = GamesModel.objects(id=id).first_or_404()

     # Create index after update
    GamesModel.create_index('name_lower', background=True)
    
    # Set data
    self.data = parse_json(game.to_json())

    return jsonify(status = "ok", data = self.data)

  # Remove weapon type by id
  def delete(self, id: str):

    # Validate id if valid
    if not ObjectId.is_valid(id):
      return {}, 400 # bad request, id is not a valid ObjectId
      
    count = GamesModel.objects(id=id).delete()
    
    return jsonify(status = "ok", count=count)