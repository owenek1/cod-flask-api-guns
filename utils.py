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

  # Filter by twitch username
  if 'twitch_username' in args.keys() and args['twitch_username'] != "": 
    query['twitch_username'] = args['twitch_username']

  # Filter by twitch profile
  if 'twitch_profile' in args.keys() and args['twitch_profile'] != "":
    query['twitch_profile'] = args['twitch_profile'].replace("\"","")

  # Filter by weapon
  if 'weapon' in args.keys() and args['weapon'] != "":
    query['weapon'] = args['weapon'].replace(" ","").replace("\"","").lower()

  # Filter by weapon id
  if 'weapon_id' in args.keys() and args['weapon_id'] != "":
    query['weapon_id'] = ObjectId(args['weapon_id'])

  # Filter by type 
  if 'type' in args.keys() and args['type'] != "":
    query['type'] = args['type'].replace(" ", "").replace("\"","").lower()

  # Filter by type id
  if 'type_id' in args.keys() and args['type_id'] != "":
    query['type_id'] = ObjectId(args['type_id'])

  # Filter by streamer id
  if 'streamer_id' in args.keys() and args['streamer_id'] != "":
    query['streamer_id'] = ObjectId(args['streamer_id'])

  # Filter by streamer
  if 'streamer' in args.keys() and args['streamer'] != "":
    query['streamer'] = args['streamer'].replace("\"", "").lower()

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
        
        if 'streamer_id' in j.keys():
          if hasattr(j['streamer_id'], 'keys'):
            if '$oid' in j['streamer_id'].keys():
              j['streamer_id'] = j['streamer_id']['$oid']
      
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

      if 'streamer_id' in jsonDump.keys():
        if hasattr(jsonDump['streamer_id'], 'keys'):
          if '$oid' in jsonDump['streamer_id'].keys():
            jsonDump['streamer_id'] = jsonDump['streamer_id']['$oid']

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