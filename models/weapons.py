from flask_mongoengine import Document
from mongoengine import StringField, ListField, IntField

class Weapons(Document):
  meta = {'collection': 'weapons'}
  name = StringField(required=True)
  name_lower = StringField(required=True)
  type_id = StringField(required=True)
  statistics = ListField(IntField(required=True))
  game_id = StringField(required=True)