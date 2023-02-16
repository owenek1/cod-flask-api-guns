
import requests, re
from bs4 import BeautifulSoup

import test_api_requests as api

from wiki_fandom_utils import parseWeaponAttachments, getWeaponAttachments, addWeaponToJsonFile

################################################       
########### Call of Duty Weapons ############### 
################################################
wikiFandom = "https://callofduty.fandom.com"
weaponsURL = wikiFandom + "/wiki/Call_of_Duty:_Modern_Warfare_(2019)#Weapons"

page = requests.get(weaponsURL)
soup = BeautifulSoup(page.content, 'html.parser')

print("... Get Call of Duty Modern Warfare weapons list from wiki fandom")

results = soup.find_all("span", {"id": "Weapons"})

for result in results: 

  weaponsTable = result.find_next("table", {"class": "mw-collapsible"})

  weaponsTr = weaponsTable.find_all("tr", {"style" : ""})

  for element in weaponsTr: 

    weaponsTd = element.find("td", {"class": "navbox-group"})

    if weaponsTd is not None:

      weaponTypeName = weaponsTd.text

      print ("Weapon type: " + weaponTypeName)

      # Request API if weapon type exists
      weaponTypeAPI = api.getWeaponTypeByName(weaponTypeName)
      weaponTypeAPI = weaponTypeAPI['data']

      if len(weaponTypeAPI) == 0:
        print("Weapon type not found!")

        addWeaponTypeChoice = input("Should we add " + weaponTypeName + " to database? ")        
        if addWeaponTypeChoice.lower() == "y":
          api.addWeaponType(weaponTypeName)

      else:
        weaponTypeAPI = weaponTypeAPI[0]
        print ("Weapon type API: " + weaponTypeAPI['name'])

        # Weapons list 
        weaponsTdList = element.find("td", {"class": "navbox-list"})

        weapons = weaponsTdList.find_all("a", href=True)

        for weapon in weapons: 
          
          weaponName = weapon.text

          print ("   Weapon name: " + weaponName)

          # Request API if weapon exists
          weaponAPI = api.getWeaponByName(weaponName)
          weaponAPI = weaponAPI['data']

          if len(weaponAPI) == 0:
            print("Weapon not found!")

            addWeaponChoice = input("Should we add " + weaponName + " to database? ")

            if addWeaponChoice.lower() == "y":
              api.addWeapon(weaponName, weaponTypeAPI['_id'])

          else:
            print ("   Weapon name API: " + weaponName)

            weaponURL = wikiFandom + weapon['href']

            weaponToAdd = {
              "name" : weaponName, 
              "url" : weaponURL,
              "type" : weaponTypeName
            }

            addWeaponToJsonFile(weaponToAdd)

            # weaponAttachmentTypesList = getWeaponAttachments(weaponURL)

            # for weaponAttachmentType in weaponAttachmentTypesList: 
            #   attachmentTypeAPI = api.getWeaponAttachmentTypeByName(weaponAttachmentType['name'])
            #   attachmentTypeAPI = attachmentTypeAPI['data']
            #   attachmentTypeId = attachmentTypeAPI[0]['_id']

            #   attachmentsList = weaponAttachmentType['attachments']

            #   weaponId = weaponAPI[0]['_id']

            #   for attachment in attachmentsList:
            #     print(api.addWeaponAttachment(attachment['name'], attachmentTypeId, weaponId, attachment['lvl_required']))

    input()

    print("############################################################")