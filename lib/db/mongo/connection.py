from flask import Flask
from flask_mongoengine import MongoEngine


from lib.log.UtilLog import UtilLog
from lib.sys.SysEnv import SysEnv


class MongoConnection:

	app = None
	mongoEngine = None

	@staticmethod
	def connect(app):
		if MongoConnection.app is not None :
			#UtilLog.warning('skip initDB app is not None')
			return

		UtilLog.debug('initDB...')
		if app is None :
			#UtilLog.debug('Using TESTING flask app to initialize db')
			app = Flask(__name__)
			app.config['TESTING'] = True

		MongoConnection.app = app

		
		UtilLog.debug('mongoEngine initializing...')
		try:
			uri		= SysEnv.get('MONGODB_URI')
			#dbname	= SysEnv.get('MONGODB_DB_NAME')
			size	= SysEnv.get('MONGODB_POOL_SIZE',1)
			#UtilLog.debug("db config dbname:%s size:%s uri:%s"%(dbname,size,uri))
			UtilLog.debug("db config size:%s uri:%s"%(size,uri))
		except Exception as e:
			UtilLog.error("MongoEngine Enviorement Error: %s"%e)
			return

		if(MongoConnection.mongoEngine is None):
			MongoConnection.mongoEngine = MongoEngine()
			#MongoConnection.app.session_interface = MongoEngineSessionInterface(MongoConnection.mongoEngine)

		MongoConnection.app.config['MONGODB_SETTINGS'] = {
			#'db':dbname,
			'host': uri,
			'connect': False,
			'maxPoolSize':size
		}
		MongoConnection.mongoEngine.init_app(app)

		if MongoConnection.app.config['TESTING'] :
			MongoConnection.app.app_context().push() # this does the binding