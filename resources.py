from flask import Flask
from flask_restful import Api

# Resources
from api.home import Home

from api.games import Games, GamesList

from api.nightbots import NightbotRegister, NightbotUnregister, NightbotUser
from api.secretResource import SecretResource  # TODO can be deleted later

from api.weaponsTest import WeaponTestsList
from api.weapons import Weapons, WeaponsList
from api.weaponTypes import WeaponTypes, WeaponTypesList
from api.weaponAttachmentTypes import WeaponAttachmentTypes, WeaponAttachmentTypesList
from api.weaponAttachments import WeaponAttachments, WeaponAttachmentsList
from api.weaponBuilds import WeaponBuilds, WeaponBuildsList

from api.users import UsersLogin, UsersRegister, TokenRefresh, UsersProfile

# Admin api
from api.nightbots import AdminNightbotsList, AdminNightbot
from api.users import AdminUsersList

from api.weapons import AdminWeaponsList, AdminWeapons

def configure_resources(app: Flask):
  api = Api(app)

  api.add_resource(Home, "/", endpoint="home")

  api.add_resource(WeaponTestsList, "/weaponsTest")

  # Games endpoints
  api.add_resource(GamesList, "/games")
  api.add_resource(Games, "/games/<string:id>")
  
  # Weapons endpoints
  api.add_resource(WeaponsList, "/weapons")
  api.add_resource(Weapons, "/weapons/<string:id>")
  
  api.add_resource(WeaponTypesList, "/weaponTypes")
  api.add_resource(WeaponTypes, "/weaponTypes/<string:id>")
  
  api.add_resource(WeaponAttachmentTypesList, "/weaponAttachmentTypes")
  api.add_resource(WeaponAttachmentTypes, "/weaponAttachmentTypes/<string:id>")
  
  api.add_resource(WeaponAttachmentsList, "/weaponAttachments")
  api.add_resource(WeaponAttachments, "/weaponAttachments/<string:id>")
  
  # Weapon builds endpoints
  api.add_resource(WeaponBuildsList, "/builds")
  api.add_resource(WeaponBuilds, "/builds/<string:id>")
  
  # User endpoints
  api.add_resource(UsersRegister, "/register")
  
  api.add_resource(UsersLogin, "/login")
  api.add_resource(TokenRefresh, "/token/refresh")
  api.add_resource(UsersProfile, "/user/profile")
  
  api.add_resource(NightbotUser, "/user/nightbot")
  
  # Admin endpoints
  api.add_resource(AdminUsersList, "/admin/users")
  
  api.add_resource(AdminNightbotsList, "/admin/nightbots")
  api.add_resource(AdminNightbot, "/admin/nightbot/<string:nightbotId>")
  
  api.add_resource(AdminWeaponsList, "/admin/weapons")
  api.add_resource(AdminWeapons, "/admin/weapons/<string:id>")
  
  # Secret resources
  api.add_resource(SecretResource, "/secret")
  
  # Nightbots
  api.add_resource(NightbotRegister, "/nightbot/register/<string:userId>")
  api.add_resource(NightbotUnregister, "/nightbot/unregister")
  
  # api.add_resource(WeaponAttachments, "/weapon/attachments/weapon/<string:weaponName>", endpoint="weaponattachmentsweaponname")
  # api.add_resource(WeaponAttachments, "/weapon/attachments/weaponid/<string:weaponId>", endpoint="weaponattachmentsweaponId")

