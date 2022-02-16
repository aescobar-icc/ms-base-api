from lib.regex.UtilRegex import UtilRegex
from lib.parser.UtilParser import UtilParser

import re
import os
class SysEnv:

	@staticmethod
	def get(env_name,def_val={},parser=None):
		val = os.environ.get(env_name)
		default_pass = def_val is not SysEnv.get.__defaults__[0]
		#print('env_name:%s def_val:%s val:%s  default_pass:%s'%(env_name,def_val,val,default_pass))
		#print(SysEnv.get.__defaults__)

		if not val and not default_pass:
			raise Exception('ENVIOREMENT VAR %s is not defined'%env_name)
		if not val :
			return def_val
		if parser:
			val = parser(val)
		return val

	@staticmethod
	def getUrl(env_name,def_val={}):

		# if not default value is provided
		# I use default from SysEnv.get, in this way SysEnv.get validate if env_name exists
		if def_val is SysEnv.getUrl.__defaults__[0]:
			def_val = SysEnv.get.__defaults__[0]

		urlText =	SysEnv.get(env_name,def_val)
		if not urlText.endswith('/'):
			urlText = urlText +'/'
		urlRegx = '(https?):\/\/((.*?)(:(\d*))?)(\/.*)'
		groups = UtilRegex.all_groups(urlRegx,urlText)

		if len(groups) == 0:
			raise Exception('env_name: %s = "%s" is not valid url'%(env_name,urlText))

		path = groups[5]
		if path.endswith('/'):
			path = path[0:len(path)-1]
		return {
			'protocol':groups[0],
			'host':groups[1],
			'hostname':groups[2],
			'port':groups[4],
			'path':path,
			'url':urlText
		}
	
	@staticmethod
	def getStartWithPrefix(prefix):
		"""
		Get all environ names that start with 'prefix'
		"""
		envNames = []
		for envName in os.environ:
			if envName.startswith(prefix) :
				envNames.append(envName)
		return envNames

	@staticmethod
	def getMatch(regex):
		"""
		Get all environ names that start with 'prefix'
		"""
		r = re.compile(regex)
		envNames = []
		for envName in os.environ:
			m = r.match(envName)
			if m :
				envNames.append(envName)
		return envNames
	
	@staticmethod
	def getBool(env_name,def_val={}):
		"""
		Get environ value as boolean 
		"""
		val = os.environ.get(env_name)
		default_pass = def_val is not SysEnv.get.__defaults__[0]

		if not val and not default_pass:
			raise Exception('ENVIOREMENT VAR %s is not defined'%env_name)
		if not val :
			return def_val
		
		return UtilParser.str2bool(val)

	@staticmethod
	def getInt(env_name,def_val=0):
		"""
		Get environ value as int 
		"""
		val = os.environ.get(env_name)
		default_pass = def_val is not SysEnv.get.__defaults__[0]

		if not val and not default_pass:
			raise Exception('ENVIOREMENT VAR %s is not defined'%env_name)
		if not val :
			if isinstance(def_val,int):
				return def_val
			return int(val)
		
		return int(val)