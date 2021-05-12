from flask import jsonify
from flask_restful import Resource

class Home(Resource): 
  def get(self):
    return jsonify(api = "Rest API Call of Duty Warzone", version = "v1.0", author="Owen", email="owenek123@gmail.com")