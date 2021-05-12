import requests, re
from bs4 import BeautifulSoup

import test_api_requests as api
import json

from wiki_fandom_utils import parseWeaponAttachments, getWeaponAttachments, getWeaponsFromJsonFiles


# Open JSON file with weapons
weapons = getWeaponsFromJsonFiles()

for weapon in weapons: 

  weaponName = weapon['name']
  weaponURL = weapon['url']

  print ("Processing " + weaponName)
  
  # Get weapon information from API
  weaponInAPI = api.getWeaponByName(weaponName)
  weaponInAPI = weaponInAPI['data'][0]

  weaponAttachmentTypesList = getWeaponAttachments(weaponURL)

  for weaponAttachmentType in weaponAttachmentTypesList: 

    attachmentTypeAPI = api.getWeaponAttachmentTypeByName(weaponAttachmentType['name'])
    attachmentTypeAPI = attachmentTypeAPI['data']

    if len(attachmentTypeAPI) > 0:
      attachmentTypeId = attachmentTypeAPI[0]['_id']

      attachmentsList = weaponAttachmentType['attachments']

      weaponId = weaponInAPI['_id']

      # Get weapon attachments from API
      weaponAttachmentsAPI = api.getWeaponAttachments(weaponId, attachmentTypeId)

      if len(weaponAttachmentsAPI) == len(attachmentsList):
        break
      else:
      
        for attachment in attachmentsList:
          print(api.addWeaponAttachment(attachment['name'], attachmentTypeId, weaponId, attachment['lvl_required']))