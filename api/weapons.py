from bson.objectid import ObjectId

from flask import current_app, request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from utils import build_query, parse_json, verify_user

from models.weapons import Weapons

# Weapons List class
class WeaponsList(Resource):
    data = []
    db = None

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

        super (WeaponsList, self).__init__()
  
    def get(self):
        # Pagination parameters
        totalPages = 0
        currentPage = 1
        totalElements = 0

        # Arguments for query
        args = self.reqparseGet.parse_args()

        # Build query to filter the db results
        query = build_query(args)

        # Filter for type
        if 'type' in query.keys():
            weaponType = self.db.weaponTypes.find_one(
                {"name_lower": query['type']})
            weaponType = parse_json(weaponType)

            if weaponType:
                query['type_id'] = ObjectId(weaponType['_id'])
                query.pop('type')

        weapons = []
        totalElements = self.db.weapons.find(query).count()

        # Pagination for the results
        if args['limit'] > 0:
            skips = args['limit'] * (args['page'] - 1)
            # { $text: { $search: "\"coffee shop\"" } }
            weapons = self.db.weapons.find(query).skip(skips).limit(args['limit'])
            totalPages = round(totalElements / args['limit'])
            currentPage = args['page']
        else:
            weapons = self.db.weapons.find(query)

        weapons = parse_json(weapons)

        # Weapon types
        inTypesQueryIds = [ObjectId(w['type_id']) for w in weapons]
        weaponTypes = self.db.weaponTypes.find(
            {"_id": {
                "$in": inTypesQueryIds
            }})
        weaponTypes = parse_json(weaponTypes)

        for w in weapons:
            weaponType = [
                weaponType for weaponType in weaponTypes
                if w['type_id'] == weaponType['_id']
            ]
            w['type'] = weaponType[0]

            # Weapon attachments
            weaponAttachments = self.db.weaponAttachments.find(
                {"weapon_id": ObjectId(w['_id'])})
            weaponAttachments = parse_json(weaponAttachments)

            availableWeaponAttachments = []

            if len(weaponAttachments) > 0:

                # Available attachment types
                weaponAttachmentTypes = self.db.weaponAttachmentTypes.find({})
                weaponAttachmentTypes = parse_json(weaponAttachmentTypes)

                for weaponAttachmentType in weaponAttachmentTypes:
                    for weaponAttachment in weaponAttachments:
                        if weaponAttachment['type_id'] == weaponAttachmentType[
                                '_id']:
                            availableWeaponAttachments.append(
                                weaponAttachmentType)
                            break

            w['available_attachments'] = availableWeaponAttachments

        self.data = weapons

        return jsonify(status="ok",
                       data=self.data,
                       totalPages=totalPages,
                       currentPage=currentPage,
                       totalElements=totalElements)


class Weapons(Resource):
    data = []
    db = None

    def __init__(self):
        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']

        super(Weapons, self).__init__()

    # Get weapon by id
    def get(self, id):

        weapons = self.db.weapons.find_one({"_id": ObjectId(id)})
        weapons = parse_json(weapons)

        # Weapon type
        if "type_id" in weapons.keys():
            weaponType = self.db.weaponTypes.find_one(
                {"_id": ObjectId(weapons['type_id'])})
            weapons['type'] = parse_json(weaponType)

        # Weapon attachments
        weaponAttachments = self.db.weaponAttachments.find(
            {"weapon_id": ObjectId(id)})
        weaponAttachments = parse_json(weaponAttachments)

        availableWeaponAttachments = []

        if len(weaponAttachments) > 0:

            # Available attachment types
            weaponAttachmentTypes = self.db.weaponAttachmentTypes.find({})
            weaponAttachmentTypes = parse_json(weaponAttachmentTypes)

            for weaponAttachmentType in weaponAttachmentTypes:
                for weaponAttachment in weaponAttachments:
                    if weaponAttachment['type_id'] == weaponAttachmentType[
                            '_id']:
                        availableWeaponAttachments.append(weaponAttachmentType)
                        break

        weapons['available_attachments'] = availableWeaponAttachments

        self.data = weapons

        return jsonify(status="ok", data=self.data)

# Admin endpoints
class AdminWeaponsList(Resource):
    data = []
    db = None
    isAdmin = True
    def __init__(self):

        self.reqparsePost = reqparse.RequestParser()
        self.reqparsePost.add_argument('name',
                                     type=str,
                                     required=True,
                                     location='json')

        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']

        super(AdminWeaponsList, self).__init__()

    # Add new weapon
    @jwt_required()
    def post(self):
        verify_user(self.isAdmin)
      
        if not request.is_json:
            return {"response": "Incorrect json"}, 500

        requestJson = request.get_json()

        print(requestJson)

        # Check if name lower field has been send
        if not "name_lower" in requestJson:
            requestJson['name_lower'] = requestJson['name'].lower().strip(
            ).replace(" ", "")

        # Check if weapon already exists
        weaponExists = self._checkWeaponExists(requestJson['name_lower'])
        if weaponExists:
            return {}, 204  # nothing to do

        # TODO check if type_id is set
        if not "type_id" in requestJson:
          return {}, 204 
          
        requestJson['type_id'] = ObjectId(requestJson['type_id'])

        if not "statistics" in requestJson:
          requestJson['statistics'] = {
                                        "accuracy" : 0,
                                        "damage" : 0,
                                        "range" : 0,
                                        "fireRate" : 0,
                                        "mobility" : 0,
                                        "control" : 0
                                      } 

        weaponAdd = self.db.weapons.insert_one(requestJson)
        weaponAddedId = weaponAdd.inserted_id

        print (weaponAddedId)

        # Find added weapon in db
        weaponAdded = self.db.weapons.find_one(
            {"_id": ObjectId(weaponAddedId)})
        data = parse_json(weaponAdded)

        return jsonify(status="ok", data=data)

    def _checkWeaponExists(self, name_lower):
        exists = False

        weapon = self.db.weapons.find_one({"name_lower": name_lower})

        if weapon:
            exists = True

        return exists


class AdminWeapons(Resource):
    data = []
    db = None
    isAdmin = True
  
    def __init__(self):
      
        self.reqparsePut = reqparse.RequestParser()
        self.reqparsePut.add_argument('name', type=str, location='json')
      
        # DB collections
        self.db = current_app.config['DB_COLLECTIONS']

        super(AdminWeapons, self).__init__()

    # Update weapons
    @jwt_required()
    def put(self, id):
        verify_user(self.isAdmin)
      
        if not request.is_json:
            return {"response": "Incorrect json"}, 500

        requestJson = request.get_json()

        if not requestJson:
            return {"response": "Incorrect json"}, 500

        # Get fields to be updated
        updateFields = self._getUpdateFields(requestJson, id)
        if not updateFields:
            return {}, 204  # nothing to do

        update = {}
        update['$set'] = updateFields

        # Update
        updateResult = self.db.weapons.update_one({"_id": ObjectId(id)},
                                                  update)
        if updateResult.matched_count == 0:
            return {
                "response": "Weapon with id {} does not exist!".format(id)
            }, 404

        # Get updated weapon
        weapon = self.db.weapons.find_one({"_id": ObjectId(id)})

        # Get weapon type
        weaponType = self.db.weaponTypes.find_one(
                {"_id": ObjectId(weapon['type_id'])})
        weapon['type'] = parse_json(weaponType)

        # Set data
        self.data = parse_json(weapon)

        return jsonify(status="ok", data=self.data)

    def _getUpdateFields(self, requestJson, weaponId):
        updateFields = {}

        # Check name field update
        if 'name' in requestJson.keys():
            requestJson['name_lower'] = requestJson['name'].lower().strip(
            ).replace(" ", "")

            updateFields['name'] = requestJson['name']
            updateFields['name_lower'] = requestJson['name_lower']

        # Check statistic fields update
        if 'statistics' in requestJson.keys():
            # By default get old values for the statistics field
            weapon = self.db.weapons.find_one({"_id": ObjectId(weaponId)})
            updateFields['statistics'] = weapon['statistics']

            # Update only the fields that are needded
            for field in requestJson['statistics']:
                value = requestJson['statistics'][field]
                updateFields['statistics'][field] = value

        # Update type id
        if 'type_id' in requestJson.keys():
            updateFields['type_id'] = ObjectId(requestJson['type_id'])

        return updateFields

    # Delete weapon
    @jwt_required()
    def delete(self, id):
      
        verify_user(self.isAdmin)

        # Find weapon and delete
        weapons = self.db.weapons.find_one_and_delete({"_id": ObjectId(id)})

        if not weapons:
            return {
                "response": "Weapon with {} does not exist!".format(id)
            }, 404

        weapons = parse_json(weapons)

        return {
            "response":
            "Weapon {} successfully deleted!".format(weapons['name'])
        }, 204
