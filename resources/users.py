from flask import request, jsonify
from flask_restful import Resource, reqparse

from passlib.apps import custom_app_context as pwd_context

from utils import build_query, parse_json

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

# db.User 
# _id = ObjectId()
# email = String
# password = String

class UsersList(Resource): 
  data = []
  usersCollection = None

  def __init__(self):

    # Get arguments
    self.reqparseGet = reqparse.RequestParser()
    self.reqparseGet.add_argument('user_id', type = str, default = 0, location = 'args')
    self.reqparseGet.add_argument('twitch_username', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('twitch_profile', type = str, default = "", location = 'args')
    self.reqparseGet.add_argument('limit', type = int, default = 0, location = 'args')

    # Post arguments 
    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('email', type=str, required=True, location='json')
    self.reqparsePost.add_argument('password', type=str, required=True, location='json')

    super(UsersList, self).__init__()

  # Get all users
  def get(self):

    # Arguments for query
    args = self.reqparseGet.parse_args()

    # Build query to filter the db results
    query = build_query(args)

    users = []
    usersTotalCount = self.usersCollection.find(query).count()
 
     # Pagination for the results
    if args['limit'] > 0:
      skips = args['limit'] * (args['page'] - 1)
      users = self.usersCollection.find(query).skip(skips).limit(args['limit'])
      totalPages = round(usersTotalCount / args['limit'])
      self.totalPages = totalPages
      self.currentPage = args['page']

      self.data = parse_json(users)

      return jsonify(status = "ok", data = self.data, totalPages = self.totalPages, currentPage = self.currentPage, totalElements=usersTotalCount)

    else:

      users = self.usersCollection.find(query)
      self.data = parse_json(users)

      return jsonify(status = "ok", data = self.data)

  def _checkUserExists(self, email):
    exists = False 

    streamer = self.usersCollection.find_one({"email" : email})

    if streamer:
      exists = True
    
    return exists

class UsersRegister(Resource):

  data = []
  usersCollection = None

  defaultRole = "user"

  def __init__(self):
    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('email', help="Email can't be empty!", type=str, required=True, location='json')
    self.reqparsePost.add_argument('password', help="Password can't be empty!", type=str, required=True, location='json')

    super(UsersRegister, self).__init__()

  def post(self):
    # Check if body json is passed
    if not request.is_json:
      return {"message" : "Incorrect json"}, 500

    # Parse request parameters
    args = self.reqparsePost.parse_args()

    # Get json data
    requestJson = request.get_json()

    requestJson['email'] = requestJson['email'].strip()
    requestJson['password'] = requestJson['password'].strip()

    # Check if the streamer already exists
    userExists = self._checkUserExists(requestJson['email'])
    if userExists: 
      return {"status" : "error", "message" : "User with {} already exists!".format(requestJson['email'])}, 201

    # Hash password for user
    requestJson['password'] = self._hashPassword(requestJson['password'])

    # Set default user role 
    requestJson['role'] = self.defaultRole

    userAdd = self.usersCollection.insert_one(requestJson)
    userAddId = userAdd.inserted_id

    if userAddId:
      return {"status" : "ok", "message" : "User registered successfully"}, 200
    else:
      return {"status" : "error", "message" : "User has not been registered!"}, 401

  def _checkUserExists(self, email):
    exists = False 

    streamer = self.usersCollection.find_one({"email" : email})

    if streamer:
      exists = True
    
    return exists

  def _hashPassword(self, password):
    return pwd_context.hash(password)

class UsersLogin(Resource):

  usersCollection = None

  def __init__(self):
    self.reqparsePost = reqparse.RequestParser()
    self.reqparsePost.add_argument('email', help="Email can't be empty!", type=str, required=True, location='json')
    self.reqparsePost.add_argument('password', help="Password can't be empty!", type=str, required=True, location='json')

    super(UsersLogin, self).__init__()

  def post(self):
    # Check if body json is passed
    if not request.is_json:
      return {"message" : "Incorrect json"}, 500

    # Parse request parameters
    args = self.reqparsePost.parse_args()

    # Get json data
    requestJson = request.get_json()

    requestJson['email'] = requestJson['email'].strip()
    requestJson['password'] = requestJson['password'].strip()

    # Check if the streamer already exists
    user = self.usersCollection.find_one({"email" : requestJson['email']})
    if not user: 
      return {"message" : "Invalid credentials"}, 401

    # Parse json
    user = parse_json(user)

    # Check if password is correct
    isPasswordCorrect = self._verifyPassword(requestJson['password'], user['password'])
    if not isPasswordCorrect:
      return {"message" : "Invalid credentials"}, 200

    # Create new tokens
    access_token = create_access_token(identity = user['email'])
    refresh_token = create_refresh_token(identity = user['email'])

    return jsonify(access_token = access_token, refresh_token = refresh_token)

  def _checkUserExists(self, email):
    exists = False 

    user = self.usersCollection.find_one({"email" : email})

    if user:
      exists = True
    
    return exists

  def _verifyPassword(self, password, hash):
    return pwd_context.verify(password, hash)

class UsersLogout(Resource):

  tokensCollection = None

  def post(self):
    pass
 
class TokenRefresh(Resource):
  @jwt_required(refresh=True)
  def post(self):
      current_user = get_jwt_identity()
      new_access_token = create_access_token(identity=current_user, fresh=False)
      return jsonify(access_token = new_access_token)
