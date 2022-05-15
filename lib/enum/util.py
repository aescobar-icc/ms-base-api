from enum import Enum
from typing import Any, Optional
class UtilEnum:

	@staticmethod
	def has_value(enum, value):
		all = enum._value2member_map_ 
		res = True if value in all else False
		print("[debug] => res:%s check if %s in %s "%(res,value,all))
		return res

	@staticmethod
	def get_by_value(enum, value):
		all = enum._value2member_map_ 
		for k,v in all.items():
			if v.value == value:
				return v
		return None
	
	@staticmethod
	def values(e: Enum) -> list:
		return list(e._value2member_map_.keys())

	
	@staticmethod
	def validate(e: Enum,values:dict) -> Optional[None]:
		for key,value in values.items():
			if not UtilEnum.has_value(e,value):
				raise Exception("%s='%s' is not present in enum %s with values=%s "%(key,value,e.__name__,UtilEnum.values(e)))
	