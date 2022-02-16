
from datetime import datetime

from json import JSONEncoder
# from bson import ObjectId
import json

class ApiEncoder(JSONEncoder):
	def default(self,obj):
		
		if isinstance(obj, datetime):
			return str(obj).replace(' ','T')+'Z'
		# if isinstance(obj, ObjectId):
		# 	return str(obj)

		return JSONEncoder.default(self, obj)