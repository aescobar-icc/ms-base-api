from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from lib.log.UtilLog import UtilLog
from lib.sys.SysEnv import SysEnv
from lib.parser.UtilParser import UtilParser


class SqlConnection:

	app = None
	sqlAlchemy = None
	sqlconnection = None

	@staticmethod
	def connect(app):
		if SqlConnection.app is not None :
			UtilLog.warning('SqlConnection skip initDB app is not None')
			return SqlConnection.sqlAlchemy

		UtilLog.debug('initDB...')
		if app is None :
			UtilLog.warning('Using TESTING flask app to initialize db')
			app = Flask(__name__)
			app.config['TESTING'] = True

		SqlConnection.app = app

		
		UtilLog.debug('SqlConnection initializing...')
		try:
			if SqlConnection.sqlAlchemy is None :
				SqlConnection.sqlAlchemy = SQLAlchemy()
		
			uri =  SysEnv.get('SQLALCHEMY_URI')
			size = SysEnv.get('SQLALCHEMY_POOL_SIZE', 5,int)
			SqlConnection.app.config['SQLALCHEMY_DATABASE_URI'] = uri
			SqlConnection.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SysEnv.get('SQLALCHEMY_TRACK_MODIFICATIONS',False,UtilParser.str2bool)
			SqlConnection.app.config['SQLALCHEMY_ECHO'] = SysEnv.get('SQLALCHEMY_ECHO',False,UtilParser.str2bool)
			SqlConnection.app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
				'pool_recycle': SysEnv.get('SQLALCHEMY_POOL_RECYCLE', 1800),
				'pool_timeout': SysEnv.get('SQLALCHEMY_POOL_TIMEOUT', 30),
				'pool_size': size,
				'max_overflow': SysEnv.get('SQLALCHEMY_MAX_OVERFLOW', 2,int),
				'pool_pre_ping': SysEnv.get('SQLALCHEMY_PRE_PING', 1) == 1,
			}
			SqlConnection.sqlAlchemy.init_app(app)

			UtilLog.debug("db config size:%s uri:%s"%(size,uri))
		except Exception as e:
			UtilLog.error("SQLALCHEMY Enviorement Error: %s"%e)
			raise e


		if SqlConnection.app.config['TESTING'] :
			SqlConnection.app.app_context().push() # this does the binding

		return SqlConnection.sqlAlchemy
	
	def getSqlAlchemy():
		if(SqlConnection.sqlAlchemy is None):
			SqlConnection.sqlAlchemy = SQLAlchemy()
		return SqlConnection.sqlAlchemy