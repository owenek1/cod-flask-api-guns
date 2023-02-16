from flask_mongoengine import Document
from mongoengine import StringField

class WeaponAttachment(Document):
    meta = {'collection': 'weaponAttachments'}
    name = StringField(required=True)
    name_lower = StringField(required=True)