from services.test.EchoService import EchoService
from lib.reflection.ApiEncoder import ApiEncoder

from flask import request,Response
import json

class EchoFacade:

	@staticmethod
	def echo(str_in):
		res = EchoService.echo(str_in)
		return Response(
			response=json.dumps(res,cls=ApiEncoder),
			status=200, 
			mimetype="application/json"
		)



