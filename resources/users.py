from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse

from passlib.apps import custom_app_context as pwd_context

from utils import build_query, parse_json

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

import datetime

# db.User 
# _id = ObjectId()
# email = String
# password = String

class UsersList(Resource): 
  data = []
  db = None

  def __init__(self):

    # Get arguments
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('search', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('user_id', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')
    self.reqparseGet.add_argument('page',  type = int, default = 1, location = 'args')
    self.reqparseGet.add_argument('role', type = str, default = "", location = 'args')

    # Post arguments 
    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('email', type=str, required=True, location='json')
    self.reqparsePost.add_argument('password', type=str, required=True, location='json')

    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(UsersList, self).__init__()

  # Get all users
  def get(self):

    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    users = []
    usersTotalCount = self.db.users.find(query).count()
 
    # Pagination for the results
    if args['limit'] > 0:
      skips = args['limit'] * (args['page'] - 1)
      users = self.db.users.find(query).skip(skips).limit(args['limit'])
      totalPages = round(usersTotalCount / args['limit'])
      self.totalPages = totalPages
      self.currentPage = args['page']

      self.data = parse_json(users)

      return jsonify(status = "ok", data = self.data, totalPages = self.totalPages, currentPage = self.currentPage, totalElements=usersTotalCount)

    else:

      users = self.db.users.find(query)
      self.data = parse_json(users)

      return jsonify(status = "ok", data = self.data)

class UsersRegister(Resource):

  db = None
  defaultRole = "user"

  def __init__(self):
    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('email', help="Email can't be empty!", type=str, required=True, location='json')
    self.reqparsePost.add_argument('password', help="Password can't be empty!", type=str, required=True, location='json')

    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(UsersRegister, self).__init__()

  def post(self):
    # Check if body json is passed
    if not request.is_json:
      return {"message" : "Incorrect json"}, 500

    # Parse request parameters
    self.reqparsePost.parse_args()

    # Get json data
    requestJson = request.get_json()

    email = requestJson['email'].strip()
    password = requestJson['password'].strip()

    # Check if the user already exists
    user = self._getUser(email)
    if user: 
      return {"message" : "User with {} is already registered!".format(email)}, 201

    # Set email
    requestJson['email'] = email

    # Hash password for user
    requestJson['password'] = self._hashPassword(password)

    # Set default user role 
    requestJson['role'] = self.defaultRole

    # Set register on date 
    requestJson['registeredOn'] = datetime.datetime.now()

    userAdd = self.db.users.insert_one(requestJson)
    userAddId = userAdd.inserted_id

    if userAddId:
      return {"status" : "ok", "message" : "User registered successfully"}, 201
    else:
      return {"status" : "error", "message" : "User has not been registered!"}, 401

  def _checkUserExists(self, email):
    exists = False 

    streamer = self.db.users.find_one({"email" : email})

    if streamer:
      exists = True
    
    return exists

  def _getUser(self, email): 
    user = self.db.users.find_one({"email" : email})

    if user:
      user = parse_json(user)

    return user

  def _hashPassword(self, password):
    return pwd_context.hash(password)

class UsersLogin(Resource):

  db = None

  def __init__(self):
    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('email', help="Email can't be empty!", type=str, required=True, location='json')
    self.reqparsePost.add_argument('password', help="Password can't be empty!", type=str, required=True, location='json')

    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(UsersLogin, self).__init__()

  def post(self):
    # Check if body json is passed
    if not request.is_json:
      return {"message" : "Incorrect json"}, 500

    # Parse request parameters
    self.reqparsePost.parse_args()

    # Get json data
    requestJson = request.get_json()

    email = requestJson['email'].strip()
    password = requestJson['password'].strip()

    # Check if exists
    user = self._getUser(email)
    if not user:
      return {"message" : "Invalid credentials"}, 401

    # Check if password is correct
    self._verifyUsersPassword(password, user['password'])

    # Create new tokens
    access_token = create_access_token(identity = user['email'])
    refresh_token = create_refresh_token(identity = user['email'])

    return jsonify(access_token = access_token, refresh_token = refresh_token)

  def _getUser(self, email): 
    user = self.db.users.find_one({"email" : email})

    if user:
      user = parse_json(user)

    return user

  def _verifyPassword(self, password, hash):
    isPasswordCorrect = pwd_context.verify(password, hash)

    if not isPasswordCorrect:
      return {"message" : "Invalid credentials"}, 401
    else:
      pass
 
class TokenRefresh(Resource):
  @jwt_required(refresh=True)
  def post(self):
      current_user = get_jwt_identity()
      new_access_token = create_access_token(identity=current_user, fresh=True)
      return jsonify(access_token = new_access_token)

class UsersProfile(Resource):
  db = None

  def __init__(self):
    # DB collections 
    self.db = current_app.config['DB_COLLECTIONS']

    super(UsersProfile, self).__init__()

  @jwt_required()
  def get(self):
    current_user_email = get_jwt_identity()

    user = self._getUser(current_user_email)

    if not user:
      return {"message" : "Invalid credentials"}, 401

    return jsonify(status = "ok", data = user)

  def _getUser(self, email): 
    user = self.db.users.find_one({"email" : email})

    if user:
      user = parse_json(user)

    return user