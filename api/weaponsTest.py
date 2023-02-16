from bson.objectid import ObjectId

from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

import cache

from utils import build_query, parse_json, verify_user

from models.weapons import Weapons

# Weapons List class
class WeaponTestsList(Resource):
  data = []

  # Pagination parameters
  totalPages = 0
  currentPage = 1
  totalElements = 0

  skip = 0
  
  def __init__(self):
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('name',
                                  type=str,
                                  default="",
                                  location='args')
    self.reqparseGet.add_argument('type',
                                  type=str,
                                  default="",
                                  location='args')
    self.reqparseGet.add_argument('game',
                                  type=str,
                                  default="",
                                  location='args')
    self.reqparseGet.add_argument('limit',
                                  type=int,
                                  default=0,
                                  location='args')
    self.reqparseGet.add_argument('page',
                                  type=int,
                                  default=1,
                                  location='args')
    self.reqparseGet.add_argument('search',
                                  type=str,
                                  default="",
                                  location='args')
    
    super (WeaponTestsList, self).__init__()

  def get(self):
    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    # Pagination
    self.totalElements = Weapons.objects.count()

    if (args['limit'] > 0):
       self.skip = args['limit'] * (args['page'] - 1)

    # Get weapons
    weapons = Weapons.objects(__raw__=query).skip(self.skip).limit(args['limit'])

    # Parse json
    self.data = parse_json(weapons.to_json())

    return jsonify(data=self.data,
                   totalPages=self.totalPages,
                   currentPage=self.currentPage,
                   totalElements=self.totalElements)
    