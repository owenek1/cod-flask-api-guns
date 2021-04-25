import sys, requests, json

BASE = "https://FlaskAPICODGUNS.pawedrabik.repl.co"

def addWeaponTypes():
  weaponTypes = [
      {"name" : "Assault"}, 
      {"name" : "Submachine"},
      {"name" : "Assault"},
      {"name" : "Submachine"},
      {"name" : "Shotgun"},
      {"name" : "LMG"},
      {"name" : "Marksman"},
      {"name" : "Sniper"},
      {"name" : "Handgun"},
      {"name" : "Launcher"},
      {"name" : "Melee"}
  ]

  for entry in weaponTypes: 
    print(entry)
    entry['name_lower'] = entry['name'].lower()
    response = requests.post(BASE + "/weapon/types", json=entry)
    print(response.json())

def addWeaponAttachmentTypes():
  attachmentTypes = [
    {"name" : "Muzzle"},
    {"name" : "Barrel"},
    {"name" : "Cable"},
    {"name" : "Arms"}, 
    {"name" : "Laser"},
    {"name" : "Optic"}, 
    {"name" : "Pumps"},
    {"name" : "Stock"},
    {"name" : "Rear Grip"}, 
    {"name" : "Bolt Assembly"},
    {"name" : "Guard"},
    {"name" : "Ammunition"},
    {"name" : "Bolt"},
    {"name" : "Trigger Action"},
    {"name" : "Pump Grip"},
    {"name" : "Underbarrel"},
    {"name" : "Perk"}
  ]

  for attachmentType in attachmentTypes: 
    print(attachmentType)
    attachmentType['name_lower'] = attachmentType['name'].strip().lower()
    response = requests.post(BASE + "/weaponAttachmentTypes", json=attachmentType)
    print(response.json())

def addWeaponAttachments(name, typeId, weaponId, lvlReq): 

  attachmentToAdd = {
    "name" : name,
    "type_id" : typeId,
    "weapon_id" : weaponId,
    "lvl_requirement" : lvlReq,
    "statistics" : {
                    "accuracy" : 0,
                    "damage" : 0,
                    "range" : 0,
                    "fireRate" : 0,
                    "mobility" : 0,
                    "control" : 0
    },
    "effects" : {"advantage" : [], 
                 "disadvantage" : []
    }
  }

  #response = requests.post(BASE + "/weapon/attachments", json=attachmentToAdd)
  #print(response.json())

  print(attachmentToAdd)

def getWeaponAttachmentTypes(): 

  weaponAttachmentTypes = [] 

  response = requests.get(BASE + "/weaponAttachmentTypes")
  jsonResponse = response.json()

  for attachmentType in jsonResponse['data']:
    weaponAttachmentTypes.append(attachmentType)

  return weaponAttachmentTypes

def deleteWeaponAttachmentTypes():

  response = requests.delete(BASE + "/weapon/attachment/types")
  print(response.json())

def deleteWeaponAttachments():
  response = requests.delete(BASE + "/weapon/attachments")
  print(response.json())

# Streamers
def addStreamer(name, username): 

  streamerToAdd = {} 

  streamerToAdd['name'] = name
  streamerToAdd['twitch_username'] = username
  streamerToAdd['twitch_profile'] = "https://www.twitch.tv/" + username

  response = requests.post(BASE + "/streamers", json=streamerToAdd)
  print(response.json())

def getStreamer(id): 
  response = requests.get(BASE + "/streamers/" + id)
  print(response.json())

def getStreamers():
  response = requests.get(BASE + "/streamers")
  print(response.json())

def deleteStreamer(id):
  response = requests.delete(BASE + "/streamers/" + id)
  print(response.json())

# Weapon builds
def addWeaponBuild(name, streamer_id, weapon_id, attachments):

  weaponBuildToAdd = {}

  weaponBuildToAdd['name'] = name 
  weaponBuildToAdd['streamer_id'] = streamer_id
  weaponBuildToAdd['weapon_id'] = weapon_id

  # Attachments list (max 5)
  weaponBuildToAdd['attachments'] = [
    '607450030e0e16bbef587eef',
    '',
    '',
    '',
    ''
  ] 

# Add user
def addUser(email, password):

  userToAdd = {}

  userToAdd['email'] = email
  userToAdd['password'] = password

  response = requests.post(BASE + "/users", json=userToAdd)
  print(response.json())