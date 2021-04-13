import sys, requests, json

from bson.objectid import ObjectId

from bs4 import BeautifulSoup

URL = 'https://gamewith.net/cod-modernwarfare/article/show/11872'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

weaponsList = []
weaponTypesList = []

BASE = "https://FlaskAPICODGUNS.pawedrabik.repl.co"

def getWeaponTypesAPI():
  response = requests.get(BASE + "/weaponTypes")

  json = response.json()
  for type in json['data']: 
    weaponTypesList.append(type)

def getWeaponType(typeToSearch):

  weaponType = None
  for type in weaponTypesList:
    if type['name_lower'] in typeToSearch.lower():
      weaponType = type
      break
  
  return weaponType

getWeaponTypesAPI()

# Get all tables with class cod_weapons
results = soup.find_all("div", {"class": "cod_weapons"})

for result in results:

  #print (dir(result))
  #print (result.prettify())

  weaponTypeElement = result.find_previous("h3").text
  weaponTypeSplitList = weaponTypeElement.split(" ")
  weaponTypeWeb = weaponTypeSplitList[0].lower()

  weaponType = getWeaponType(weaponTypeWeb)

  if weaponType is not None:
    td_elements = result.find_all("td")

    for elem in td_elements:
      
      img = elem.find("img")

      if img is not None:

        weaponName = img.get("alt")
        weaponImage = img.get("data-original")
        weaponNameLower = weaponName.lower().strip().replace(" ", "")

        weapon = {
                    "name" : weaponName, 
                    "name_lower" : weaponNameLower, 
                    "type_id" : weaponType['_id'],
                    "statistics": {
                                    "accuracy" : 0,
                                    "damage" : 0,
                                    "range" : 0,
                                    "fireRate" : 0,
                                    "mobility" : 0,
                                    "control" : 0
                                  }
                }

        weaponsList.append(weapon)

# Add weapons through API
for entry in weaponsList:
  response = requests.post(BASE + "/weapons", json=entry)
  print(response.json())


  

