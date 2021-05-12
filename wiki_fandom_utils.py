import requests, re
from bs4 import BeautifulSoup

import test_api_requests as api

import json

def addWeaponToJsonFile(weapon):
  f = open('weapons.json', "r")

  j = json.load(f)

  f.close()

  # Get weapons
  weapons = j['weapons']

  # Add new weapon
  weapons.append(weapon)

  # Clear file
  open('weapons.json', 'w').close()

  # Dump json to file
  f = open('weapons.json', 'w')

  f.write(json.dumps({"weapons" : weapons} , sort_keys=False, indent=4))

  f.close()

def getWeaponsFromJsonFiles(): 

  f = open('weapons.json', "r")

  j = json.load(f)

  f.close()

  weapons = j['weapons']

  return weapons

def parseWeaponAttachments(results, tag="h3"):
  attachmentTypesList = []

  for result in results: 
    attachmentTypes = result.find_all_next(tag)

    for attachmentElement in attachmentTypes:

      attachmentTypeName = attachmentElement.text

      weaponAttachmentsListUL = attachmentElement.findNextSibling()

      #print("      " + attachmentTypeName)

      attachmentsList = []

      if weaponAttachmentsListUL is not None: 

        weaponAttachmentsListLI = weaponAttachmentsListUL.findChildren("li")
        
        for weaponAttachment in weaponAttachmentsListLI:

          # Check if Lv. or Level is in the name
          if "Level" in weaponAttachment.text:
            splitAttachmentName = weaponAttachment.text.split('(Level ')
          else:
            splitAttachmentName = weaponAttachment.text.split('(Lv.')

          attachmentName = splitAttachmentName[0].replace(u'\xa0', u'')
          attachmentLvlReq = 0

          if len(splitAttachmentName) > 1: 
            attachmentLvlReq = splitAttachmentName[1].replace(")", "").replace(" ","").replace('\u200b','')

          attachmentsList.append({"name" : attachmentName, "lvl_required" : int(attachmentLvlReq)})
      
      attachmentType = {"name" : attachmentTypeName, "attachments" : attachmentsList} 
      attachmentTypesList.append(attachmentType)

  return attachmentTypesList

def getWeaponAttachments(weaponURL):
  
  page = requests.get(weaponURL)
  soup = BeautifulSoup(page.content, 'html.parser')

  attachmentTypesList = []

  spanCodModernWarfare = soup.find("span", {"id": "Call_of_Duty:_Modern_Warfare"})

  if spanCodModernWarfare is None:
    results = soup.find_all("span", {"id": "Attachments"})
    if results is not None:
      attachmentTypesList = parseWeaponAttachments(results)
  else:
    results = spanCodModernWarfare.find_next("h3", text=re.compile("Attachments"))
    if results is not None:
      attachmentTypesList = parseWeaponAttachments(results, "h4")
  
  return attachmentTypesList
        