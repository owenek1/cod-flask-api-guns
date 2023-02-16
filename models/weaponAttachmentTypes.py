from flask_mongoengine import Document
from mongoengine import StringField

class WeaponAttachmentType(Document):
    meta = {'collection': 'weaponAttachmentTypes'}
    name = StringField(required=True)
    name_lower = StringField(required=True)