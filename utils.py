from bson import json_util
from bson.objectid import ObjectId

import json

def build_query(args):

  query = {}

  # Search regex
  if 'search' in args.keys() and args['search'] != "":
    nameToLower = args['search'].replace(" ","").replace("\"","").lower()
    query['name_lower'] = { "$regex": nameToLower }

  # Filter by name
  if 'name' in args.keys() and args['name'] != "":
    query['name_lower'] = args['name'].replace(" ","").replace("\"","").lower()

  # Filter by role
  if 'role' in args.keys() and args['role'] != "":
    query['role'] = args['role'].replace(" ","").replace("\"","").lower()

  # Filter by weapon
  if 'weapon' in args.keys() and args['weapon'] != "":
    query['weapon'] = args['weapon'].replace(" ","").replace("\"","").lower()

  # Filter by type 
  if 'type' in args.keys() and args['type'] != "":
    query['type'] = args['type'].replace(" ", "").replace("\"","").lower()

  # Filter by user
  if 'user' in args.keys() and args['user'] != "": 
    query['user'] = args['user'].replace(" ", "").replace("\"","").lower()

  # Filter by weapon id
  if 'weapon_id' in args.keys() and args['weapon_id'] != "":
    query['weapon_id'] = ObjectId(args['weapon_id'])

  # Filter by type id
  if 'type_id' in args.keys() and args['type_id'] != "":
    query['type_id'] = ObjectId(args['type_id'])

  # Filter by user id
  if 'user_id' in args.keys() and args['user_id'] != "":
    query['user_id'] = ObjectId(args['user_id'])

  return query

def parse_json(data):
  """Replace ObjectId to string"""
  jsonDump = json.loads(json_util.dumps(data))

  if isinstance(jsonDump, list):
    
    for j in jsonDump:

      if hasattr(j, 'keys'):
        
        if '_id' in j.keys():
          if hasattr(j['_id'], 'keys'):
            if '$oid' in j['_id'].keys():
              j['_id'] = j['_id']['$oid']

        if 'type_id' in j.keys():
          if hasattr(j['type_id'], 'keys'):
            if '$oid' in j['type_id'].keys():
              j['type_id'] = j['type_id']['$oid']

        if 'weapon_id' in j.keys():
          if hasattr(j['weapon_id'], 'keys'):
            if '$oid' in j['weapon_id'].keys():
              j['weapon_id'] = j['weapon_id']['$oid']

        if 'user_id' in j.keys():
          if hasattr(j['user_id'], 'keys'):
            if '$oid' in j['user_id'].keys():
              j['user_id'] = j['user_id']['$oid']

        if 'type' in j.keys():
          if hasattr(j['type'], 'keys'):
            if hasattr(j['type']['_id'], 'keys'):
              if '$oid' in j['type']['_id'].keys():
                j['type']['_id'] = j['type']['_id']['$oid']

        if 'attachments' in j.keys():
          if isinstance(j['attachments'], list):
            attachments = []
            for a in j['attachments']:
              if '$oid' in a.keys():
                attachments.append(a['$oid'])
            j['attachments'] = attachments
  else:

    if hasattr(jsonDump, 'keys'):

      if '_id' in jsonDump.keys():
        if hasattr(jsonDump['_id'], 'keys'):
          if '$oid' in jsonDump['_id'].keys():
            jsonDump['_id'] = jsonDump['_id']['$oid']

      if 'type_id' in jsonDump.keys():
        if hasattr(jsonDump['type_id'], 'keys'):
          if '$oid' in jsonDump['type_id'].keys():
            jsonDump['type_id'] = jsonDump['type_id']['$oid']

      if 'weapon_id' in jsonDump.keys():
        if hasattr(jsonDump['weapon_id'], 'keys'):
          if '$oid' in jsonDump['weapon_id'].keys():
            jsonDump['weapon_id'] = jsonDump['weapon_id']['$oid']

      if 'user_id' in jsonDump.keys():
        if hasattr(jsonDump['user_id'], 'keys'):
          if '$oid' in jsonDump['user_id'].keys():
            jsonDump['user_id'] = jsonDump['user_id']['$oid']

      if 'type' in jsonDump.keys():
        if hasattr(jsonDump['type'], 'keys'):
            if hasattr(jsonDump['type']['_id'], 'keys'): 
              if '$oid' in jsonDump['type']['_id']:
                jsonDump['type']['_id'] = jsonDump['type']['_id']['$oid']

      if 'attachments' in jsonDump.keys():
          if isinstance(jsonDump['attachments'], list):
            attachments = []
            for a in jsonDump['attachments']:
              if '$oid' in a.keys():
                attachments.append(a['$oid'])
            jsonDump['attachments'] = attachments

  return jsonDump