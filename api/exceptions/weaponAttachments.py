from werkzeug.exceptions import HTTPException

class WeaponAttachments(HTTPException):
    code = 404
    data = {"message": "Recipe not found"}