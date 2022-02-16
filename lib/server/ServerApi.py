## ##############################################################
## @author: Adán Escobar
## @mail: aescobar@codeits.cl
## ##############################################################
from flask import request,Response
from flask_cors import CORS
import connexion
import traceback
import json


from lib.sys.SysEnv import SysEnv
from lib.log.UtilLog import UtilLog
from lib.mail.UtilMail import UtilMail
from lib.response.ResponseApi import ResponseApi
from lib.service.UtilService import UtilService
from lib.reflection.UtilReflection import UtilReflection
from lib.reflection.ApiEncoder import ApiEncoder

from glob import glob
from os import path
class ServerApi:
	app = None
	useDB = True
	@staticmethod
	def init():
		SYS_API_PATH = SysEnv.get("SYS_API_PATH","/api-run/apis")
		SYS_API_FILE_PREFIX = SysEnv.get("SYS_API_FILE_PREFIX","api_")
		ServerApi.useDB = SysEnv.getBool("SYS_USE_DB",True)
		# Create the application instance
		connx_app = connexion.App(__name__, specification_dir=SYS_API_PATH,server='gevent')

		#getting flask app
		app = connx_app.app
		app.url_map.strict_slashes = False
		CORS(app, resources={r"*": {"origins": "*"}}) 

		# Read the swagger.yml file to configure the endpoints
		pattern = "%s/%s*.yaml"%(SYS_API_PATH,SYS_API_FILE_PREFIX)
		files = [path.basename(x) for x in glob(pattern)]
		if len(files) > 0:
			for api_yaml in files:
				try:
					#connx_app.add_api('server_api.yaml')
					connx_app.add_api(api_yaml)
					UtilLog.info("%s successfully loaded!"%(api_yaml))
				except Exception as e:
					UtilLog.error("Error loading %s EXCEP:%s "%(api_yaml,e))
					#raise e
		else:
			UtilLog.warning("no apis was found at: %s"%pattern)

		return app


		

	@staticmethod
	def before_request(request):
		pass

	@staticmethod
	def after_request(response):
		#to avoid swagger validation format response
		UtilLog.debug('status:%s mimetype:%s'%(response.status,response.mimetype))
		if not isinstance(response,ResponseApi) and response.status_code >= 400 :
			res = {}
			if response.mimetype == "application/json" or response.mimetype == "application/problem+json":
				if isinstance(response.response,list):
					res = json.loads(response.response[0])
				else:
					res = json.loads(response.response)
			status_code = response.status_code
			message = response.status
			if 'status' in res:
				status_code = res['status']
			if 'detail' in res:
				message = res['detail']

			UtilLog.warning(message)
			return Response(
					response=json.dumps({'message':message, 'status':status_code}), 
					status=status_code,
					mimetype="application/problem+json"
			)
		elif response.status_code >= 300 :
			try:
				UtilLog.debug({
					"response":response.response,
					"status":response.status_code,
					"mimetype":response.mimetype})
			except:
				pass
		return response

	@staticmethod
	def errorhandler(error):

		#getting error code and message
		status_code = int(getattr(error, 'status_code', 500))
		message		= getattr(error, 'message', 'Server Internal Error: %s'%str(error))
		at_field	= getattr(error, 'field_name', '')
		error_code  = getattr(error, 'error_code', 'N/A')
		exceptionData  = getattr(error, 'exceptionData', None)

		if at_field is not None and at_field != '':
			message += ' at field ' + at_field

		if status_code >= 500:
			#getting and printing stacktrace
			UtilLog.error(message)

			trace = traceback.format_exc()
			traceback.print_exc()
			#sending error mail
			UtilMail.sendError(request,'%s\n%s'%(str(error),trace))

		resp = {'message':message, 'status':status_code}

		if error_code!= 'N/A':
			resp['error_code']=error_code
		if exceptionData is not None:
			resp['exceptionData']= exceptionData

		return ResponseApi(
				response=json.dumps(resp,cls=ApiEncoder), 
				status=status_code
		)


	@staticmethod
	def fake_decode(token):
		#UtilLog.debug("fake_decode %s"%(token))
		return {}
	# def fake_validate_scope(required_scopes, token_scopes):
	# 	UtilLog.debug("fake_validate_scope %s %s"%(required_scopes, token_scopes))
	# 	return True

		
