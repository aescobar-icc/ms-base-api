from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

import psycopg2


from lib.log.UtilLog import UtilLog
from lib.sys.SysEnv import SysEnv
from lib.parser.UtilParser import UtilParser


class SqlConnection:

    app = None
    uri=None
    sqlAlchemy = None
    sqlconnection = None
    
    create_pending=False

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
        
            SqlConnection.uri =  SysEnv.get('SQLALCHEMY_URI')
            size = SysEnv.get('SQLALCHEMY_POOL_SIZE', 5,int)
            SqlConnection.app.config['SQLALCHEMY_DATABASE_URI'] = SqlConnection.uri
            SqlConnection.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SysEnv.get('SQLALCHEMY_TRACK_MODIFICATIONS',False,UtilParser.str2bool)
            SqlConnection.app.config['SQLALCHEMY_ECHO'] = SysEnv.get('SQLALCHEMY_ECHO',False,UtilParser.str2bool)
            SqlConnection.app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_recycle': SysEnv.get('SQLALCHEMY_POOL_RECYCLE', 1800),
                'pool_timeout': SysEnv.get('SQLALCHEMY_POOL_TIMEOUT', 30),
                'pool_size': size,
                'max_overflow': SysEnv.get('SQLALCHEMY_MAX_OVERFLOW', 2,int),
                'pool_pre_ping': SysEnv.get('SQLALCHEMY_PRE_PING', 1) == 1,
            }
            UtilLog.debug('SqlConnection init_app...')
            SqlConnection.sqlAlchemy.init_app(app)
            
            UtilLog.debug("db config size:%s uri:%s"%(size,SqlConnection.uri))
        except Exception as e:
            UtilLog.error("SQLALCHEMY Enviorement Error: %s"%e)
            raise e


        if SqlConnection.app.config['TESTING'] :
            SqlConnection.app.app_context().push() # this does the binding
            
        
        if SqlConnection.create_pending:
            SqlConnection.create_all()

        return SqlConnection.sqlAlchemy
    
    def getSqlAlchemy():
        if(SqlConnection.sqlAlchemy is None):
            UtilLog.debug('SqlConnection getSqlAlchemy is NONE ...')
            SqlConnection.sqlAlchemy = SQLAlchemy()
        return SqlConnection.sqlAlchemy
    
    def create_all():
        if SqlConnection.app is None:
            SqlConnection.create_pending=True
            return
        try:
            url="/".join(SqlConnection.uri.split('/')[0:-1])+"/postgres"
            database=SqlConnection.uri.split('/')[-1]
            
            UtilLog.debug('SqlConnection conecting to: "{0}" '.format(url))
            engine = create_engine(url)

            UtilLog.debug('SqlConnection create db: "{0}" if not exists...'.format(database))
            conn = engine.connect()
            conn.execute("commit")
            conn.execute(f"CREATE DATABASE {database}")
            #db_engine = create_engine(SqlConnection.uri)
        
        # except psycopg2.errors.DuplicateDatabase as e:
        #     #ignore database already exists
        #     pass
        except Exception as e:
            UtilLog.error('SqlConnection create db ERROR:'+str(e))
          
        try:      

            with SqlConnection.app.app_context():
                UtilLog.debug('SqlConnection create tables ...')
                SqlConnection.sqlAlchemy.create_all()
        except Exception as e:
            UtilLog.error('SqlConnection create tables ERROR:'+str(e))