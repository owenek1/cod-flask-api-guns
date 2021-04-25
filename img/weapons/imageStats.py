from os import listdir
from os.path import isfile, join
from PIL import Image

submachinesWeaponPath = "submachine"

submachineImageFiles = [f for f in listdir(submachinesWeaponPath) if isfile(join(submachinesWeaponPath, f))]

for img in submachineImageFiles:
  imagePath = join(submachinesWeaponPath, img)
  imageOpen = Image.open(imagePath).convert('L')
  imageOpen.save(img) 