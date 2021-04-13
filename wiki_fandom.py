
import sys, requests
from bs4 import BeautifulSoup

from test_api_requests import getWeaponAttachmentTypes, addWeaponAttachments

weaponM13URL = "https://callofduty.fandom.com/wiki/M13"
weaponAK47URL = "https://callofduty.fandom.com/wiki/AK-47"
m13WeaponId = "6071dfd0e6546c380f42003b"
ak47WeaponId = "6071dfd1e6546c380f42003e"

page = requests.get(weaponAK47URL)

soup = BeautifulSoup(page.content, 'html.parser')

# Get weapon attachments from API
weaponAttachmentTypes = []
weaponAttachmentTypes = getWeaponAttachmentTypes()

print("... API weapon attachments " + str(len(weaponAttachmentTypes)))

# Get all tables with class cod_weapons
results = soup.find_all("span", {"id": "Attachments"})

for result in results: 

  attachmentElements = result.find_all_next("h3")

  for element in attachmentElements: 

    if "[edit | edit source]" in element.text:

      attachmentType = element.text.split('[edit | edit source]')[0]

      print("... " + attachmentType)  

      attachmentTypeAPI = None
      for attachmentTypeApi in weaponAttachmentTypes: 
        if attachmentType == attachmentTypeApi['name']:
          print("found attachment type in api " + attachmentType)
          attachmentTypeAPI = attachmentTypeApi
          break
      
      if attachmentTypeAPI is None: 
        print("Did not find attachment type " + attachmentType)
        break

      attachmentsUl = element.find_next("ul")

      for attachmentUl in attachmentsUl.findChildren("li"): 
        #print (dir(attachmentsUl))
        
        #print (attachmentUl)
        attachmentName = attachmentUl.text

        splitAttachmentName = attachmentUl.text.split('(Lv.')

        attachmentName = splitAttachmentName[0].replace(u'\xa0', u'')

        attachmentLvlReq = ""
        if len(splitAttachmentName) > 1: 
          attachmentLvlReq = splitAttachmentName[1].replace(")", "").replace(" ","")

        # Add attachment to API
        addWeaponAttachments(attachmentName, attachmentTypeAPI['_id'], m13WeaponId, attachmentLvlReq)

perks = result.find_next("h2")
perksUl = perks.find_next("ul")

attachmentTypeAPI = None
for attachmentTypeApi in weaponAttachmentTypes: 
  if "Perk" == attachmentTypeApi['name']:
    print("found attachment type in api " + attachmentType)
    attachmentTypeAPI = attachmentTypeApi
    break

for attachmentUl in perksUl.findChildren("li"):

  attachmentName = attachmentUl.text

  splitAttachmentName = attachmentUl.text.split('(Lv.')

  attachmentName = splitAttachmentName[0].replace(u'\xa0', u'')

  attachmentLvlReq = ""
  if len(splitAttachmentName) > 1: 
    attachmentLvlReq = splitAttachmentName[1].replace(")", "").replace(" ","")

  addWeaponAttachments(attachmentName, attachmentTypeAPI['_id'], m13WeaponId, attachmentLvlReq)