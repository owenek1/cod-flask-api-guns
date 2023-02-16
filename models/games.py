from flask_mongoengine import Document
from mongoengine import StringField

class Games(Document):
  name = StringField(required=True)
  name_lower = StringField(required=True)