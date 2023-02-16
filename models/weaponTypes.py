from flask_mongoengine import Document
from mongoengine import StringField, ListField

class WeaponTypes(Document):
  meta = {'collection': 'weaponTypes'}
  name = StringField(required=True)
  name_lower = StringField(required=True)
  game_ids = ListField(StringField(required=True))