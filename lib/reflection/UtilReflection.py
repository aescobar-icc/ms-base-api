## ##############################################################
## @author: Adán Escobar
## @mail: aescobar.icc@gmail.com
## ##############################################################
import sys
import os
import subprocess
import re

import collections.abc
import importlib

from lib.log.UtilLog import UtilLog
from lib.exceptions.ExceptionApi import ExceptionApi
from lib.regex.UtilRegex import UtilRegex

class UtilReflection:

	@staticmethod
	def get_value(data,path,raiseExc=True):
		path = path.split(".")
		rec=''
		obj = data
		for key in path:
			try:
				rec+=key+"."
				indexes = UtilRegex.all_matches("\[(.*?)\]",key) # example: abc_01[x][y][z] => indexes:['x','y','z']
				if len(indexes)>0: #if it is a array expression
					key = UtilRegex.all_matches("^([a-zA-Z_0-9]*)",key)[0] # example: abc_01[x][y][z] => key:abc_01
					obj=obj[key]
					for i in indexes:
						literal = UtilRegex.all_matches("^'(.*?)'$",i)
						if len(literal)>0:
							i = literal[0]
						else:
							i = int(i)
						obj=obj[i]
				else:
					obj=obj[key]
				
			except Exception as e:
				msg = '[UtilReflection] dict: %s do not contain key : "%s" EXC:%s'%(data,rec,e)
				if raiseExc:
					raise Exception(msg)
				UtilLog.debug(msg)
				return None
			
		return obj
	@staticmethod
	def set_value(obj,path,value):
		path = path.split(".")
		try:
			for key in path[:-1]:
				if key not in obj:
					obj[key] = {}
				obj=obj[key]
			obj[path[-1]]=value
		except Exception as e:
			raise Exception('error setting key : "%s" in obj:%s caused by %s'%(path,str(obj),e))

	
	@staticmethod
	def load_script(script,globalsParameter = {},localsParameter = {}):
		if hasattr(script, 'read'):
			script = script.read().decode("utf-8") 
		exec(script, globalsParameter, localsParameter)
		return localsParameter
	@staticmethod
	def call_operation(operation,args):
		try:
			arr = operation.split(".")
			method = arr.pop()
			clss =  ".".join(arr)
			UtilLog.warning( "%s.%s"%(clss,method))
			clss = UtilReflection.load_class_by_name(clss)

			method = getattr(clss, method)

			return method(*args)
		except ExceptionApi as e:
			raise e
		except Exception as e:
			raise ExceptionApi(400,"Error calling operation:%s EXC:%s"%(operation,e))
			
	@staticmethod
	def loadsImports(imports):
		loaded = {}
		for clss_path in imports:
			clss = UtilReflection.load_class_by_name(clss_path)
			loaded[clss_path.split(".").pop()] = clss
		#UtilLog.debug(loaded)
		return loaded
	clss_cache = {}
	@staticmethod
	def load_class_by_name(clss_path):
		if clss_path in UtilReflection.clss_cache:
			UtilLog.debug('class:%s from cache'%clss_path)
			return UtilReflection.clss_cache[clss_path]
		if "." in clss_path:
			imp = clss_path.split('.')
			clssName = imp[-1]
			module = imp[-2]
			namespace = '.'.join(imp[:-1])
			module = importlib.import_module(namespace)
			clss = getattr(module, clssName)
			UtilReflection.clss_cache[clss_path] = clss
			return clss
		else:
			return importlib.import_module(clss_path)
	@staticmethod
	def update(d, u):
		for k, v in u.items():
			if isinstance(v, collections.abc.Mapping):
				d[k] = UtilReflection.update(d.get(k, {}), v)
			else:
				d[k] = v
		return d


	@staticmethod
	def dict_in_array(array,key,value):
		"""
			Check if a dict is constains in array by a value key
		"""
		for item in array:
			if key in item and item[key] == value:
				return True
		return False


	@staticmethod
	def pip_freeze():
		sp = subprocess.run(["pip", "freeze"], stdout=subprocess.PIPE)
		return sp.stdout.decode('utf-8').split('\n')
	@staticmethod
	def lib_version(lib_name):
		sp = subprocess.run(["pip3", "show", lib_name], stdout=subprocess.PIPE)
		ver = sp.stdout.decode('utf-8').strip().split('\n')[1]
		res = re.search('^Version:\ (.*)$', ver)
		return res.group(1)

	@staticmethod
	def match(obj,eval):
		for key, value in eval:
			if UtilReflection.get_value(obj,key) != value:
				return False

		return True

	@staticmethod
	def only(object,keys):
		"""
		Create a sub dict with certain keys. Supports nested keys

		How to use:
		----------

			`obj = { "a":1, "b":{"c":2,"d":3}, "z"}`

			`sub = UtilReflection.only(obj,["a","b.c"])`
			
			`sub => {'a': 1, 'b': {'c': 2}}`
		"""
		obj = {}
		for path in keys:
			origin = object
			target = obj
			#support for full key value
			if path in target:
				continue
			if path in origin:
				obj[path] = origin[path]
				continue

			paths = path.split(".")
			rec=''
			for key in paths:
				rec += key
				if key in target:
					target = target[key]
					origin = origin[key]
					rec += '.'
					continue
				if key in origin:
					#print(" %s %s "%(rec,path))
					if rec == path:
						target[key] = origin[key]
					else:
						target[key] = {}
					target = target[key]
					origin = origin[key]
					rec += '.'
				else:
					target[key] = None
					break
		return obj
