from flask_mongoengine import Document
from mongoengine import StringField

class WeaponBuilds(Document):
  meta = {'collection': 'weaponBuilds'}
  name = StringField(required=True)
  name_lower = StringField(required=True)
