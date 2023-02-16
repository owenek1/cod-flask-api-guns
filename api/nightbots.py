from bson.objectid import ObjectId
from datetime import datetime

from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from utils import build_query, parse_json, verify_user

class NightbotUser(Resource):
    db = None

    def __init__(self):
        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']

        super(NightbotUser, self).__init__()

    @jwt_required()
    def get(self):
        user = verify_user()

        nightbot = self.db.nightbots.find_one(
            {"user_id": ObjectId(user['_id'])})

        return jsonify(status="ok", data=parse_json(nightbot))


class NightbotRegister(Resource):
    db = None
  
    def __init__(self):
        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']
        super(NightbotRegister, self).__init__()

    def get(self, userId):
        requestHeaders = request.headers

        # Process nightbot information
        # Example of Nightbot-Channel header
        # Nightbot-Channel: name=night&displayName=Night&provider=twitch&providerId=11785491
        if not "Nightbot-Channel" in requestHeaders.keys():
            return {"message": "Invalid request"}, 400

        nightbotChannelHeader = requestHeaders['Nightbot-Channel']
        nightbotInfo = nightbotChannelHeader.split("&")
        nightbotInfoList = {
            "name": "",
            "displayName": "",
            "provider": "",
            "providerId": 0
        }

        for info in nightbotInfo:
            infoSplit = info.split("=")

            field = infoSplit[0]
            value = infoSplit[1]

            nightbotInfoList[field] = value

        # Check if user with that id is registered and can register a nightbot
        user = self.db.users.find_one({"_id": ObjectId(userId)})
        user = parse_json(user)

        if len(user) == 0:
            return {"message": "User not found!"}, 201

        # Check if nighbot already registered for the user
        nightbotCheck = self.db.nightbots.find_one(
            {"user_id": ObjectId(userId)})
        nightbotCheck = parse_json(nightbotCheck)

        if nightbotCheck is not None:
            # Nightbot already registered for this user
            return {"message": "Nightbot already registered!"}, 201

        data = {}

        # Register nightbot for the user
        data['user_id'] = ObjectId(userId)
        data['registered_on'] = datetime.now().strftime("%Y-%m-%d")
        data['provider'] = nightbotInfoList['provider']
        data['provider_id'] = nightbotInfoList['providerId']
        data['is_active'] = True

        nightbotRegister = self.db.nightbots.insert_one(data)
        nightbotRegisterId = nightbotRegister.inserted_id

        nightbot = self.db.nightbots.find_one(
            {"_id": ObjectId(nightbotRegisterId)})

        if nightbot is None:
            return {
                "message":
                "Nightbot could not be registered in CoD API Weapons!"
            }, 400

        return {
            "message": "Nightbot registered successfully in CoD API Weapons!"
        }, 200


class NightbotUnregister(Resource):
    db = None

    def __init__(self):
        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']
        super(NightbotUnregister, self).__init__()

    def get(self):

        requestHeaders = request.headers

        # Process nightbot information
        # Example of Nightbot-Channel header
        # Nightbot-Channel: name=night&displayName=Night&provider=twitch&providerId=11785491
        if not "Nightbot-Channel" in requestHeaders.keys():
            return {"message": "Invalid request"}, 400

        nightbotChannelHeader = requestHeaders['Nightbot-Channel']
        nightbotInfo = nightbotChannelHeader.split("&")
        nightbotInfoList = {
            "name": "",
            "displayName": "",
            "provider": "",
            "providerId": 0
        }

        for info in nightbotInfo:
            infoSplit = info.split("=")

            field = infoSplit[0]
            value = infoSplit[1]

            nightbotInfoList[field] = value

        # Check if nighbot registered
        self.db.nightbots.find_one_and_update(
            {"provider_id": nightbotInfoList['providerId']},
            {"$set": {
                "is_active": False
            }})

        return {
            "message":
            "Nightbot unregistered successfully from CoD API Weapons!"
        }, 200


# Admin resource endpoints
class AdminNightbotsList(Resource):
    db = None
    isAdmin = True

    def __init__(self):
        self.reqparseGet = reqparse.RequestParser()
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

        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']
        super(AdminNightbotsList, self).__init__()

    @jwt_required()
    def get(self):

        # Get user and verify isAdmin
        user = verify_user(self.isAdmin)

        # Pagination parameters
        totalPages = 0
        currentPage = 1
        totalElements = 0

        # Arguments for query
        args = self.reqparseGet.parse_args()

        # Build query to filter the db results
        query = build_query(args)

        nightbots = []
        totalElements = self.db.nightbots.find(query).count()

        if args['limit'] > 0:
            skips = args['limit'] * (args['page'] - 1)
            # { $text: { $search: "\"coffee shop\"" } }
            nightbots = self.db.weapons.find(query).skip(skips).limit(
                args['limit'])
            totalPages = round(totalElements / args['limit'])
            currentPage = args['page']
        else:
            nightbots = self.db.nightbots.find(query)

        nightbots = parse_json(nightbots)

        for nightbot in nightbots:
            user = self.db.users.find_one(
                {"_id": ObjectId(nightbot['user_id'])})
            nightbot['user'] = parse_json(user)

        return jsonify(status="ok",
                       data=parse_json(nightbots),
                       totalElements=totalElements,
                       totalPages=totalPages,
                       currentPage=currentPage)


class AdminNightbot(Resource):

    db = None
    isAdmin = True

    def __init__(self):
        self.reqparsePost = reqparse.RequestParser()
        self.reqparsePost.add_argument('provider',
                                       type=str,
                                       required=True,
                                       location='json')
        self.reqparsePost.add_argument('provider_id',
                                       type=str,
                                       required=True,
                                       location='json')
        self.reqparsePost.add_argument('user_id',
                                       type=str,
                                       required=True,
                                       location='json')

        self.reqparsePut = reqparse.RequestParser()
        self.reqparsePut.add_argument('provider',
                                      type=str,
                                      default="",
                                      location='json')
        self.reqparsePut.add_argument('provider_id',
                                      type=str,
                                      default="",
                                      location='json')
        self.reqparsePut.add_argument('user_id',
                                      type=str,
                                      default="",
                                      location='json')
        self.reqparsePut.add_argument('is_active',
                                      type=bool,
                                      default="",
                                      location='json')

        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']
        super(AdminNightbot, self).__init__()

    @jwt_required()
    def get(self, nightbotId):

        # Validate user if admin
        verify_user(self.isAdmin)

        # Validate Id
        if not ObjectId.is_valid(nightbotId):
            return {}, 400  # bad request, id is not a valid ObjectId

        nightbot = self.db.nightbots.find_one({"_id": ObjectId(nightbotId)})

        if nightbot is None:
            return {}, 404

        nightbot = parse_json(nightbot)

        # Get nightbot user
        nightbotUser = self.db.users.find_one(
            {"_id": ObjectId(nightbot['user_id'])})

        nightbot['user'] = parse_json(nightbotUser)

        return jsonify(status="ok", data=nightbot)

    @jwt_required()
    def put(self, nightbotId):

        args = self.reqparsePut.parse_args()

        print(args)

        # Validate user if admin
        verify_user(self.isAdmin)

        # Validate Id
        if not ObjectId.is_valid(nightbotId):
            return {}, 400  # bad request, id is not a valid ObjectId

        updateFields = self._getUpdateFields(args)

        if updateFields == {}:
            return {}, 201  # nothing to do

        update = {}
        update['$set'] = updateFields

        # Update
        updateResult = self.db.nightbots.update_one(
            {"_id": ObjectId(nightbotId)}, update)
        if updateResult.matched_count == 0:
            return {}, 404

        # Get updated weapon
        nightbot = self.db.nightbots.find_one({"_id": ObjectId(nightbotId)})
        nightbot = parse_json(nightbot)

        # Get nightbot user
        nightbotUser = self.db.users.find_one(
            {"_id": ObjectId(nightbot['user_id'])})
        nightbot['user'] = parse_json(nightbotUser)

        return jsonify(status="ok", data=nightbot)

    def _getUpdateFields(self, args):

        update = {}
        argKeys = args.keys()

        for key in argKeys:
            if args[key] != "":
                update[key] = args[key]

        return update
