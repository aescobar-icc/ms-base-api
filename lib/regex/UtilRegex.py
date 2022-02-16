## ##############################################################
## @author: Adán Escobar
## @mail: aescobar.icc@gmail.com
## ##############################################################

import re
class UtilRegex:
	@staticmethod
	def all_matches(regex,text):
		r = re.compile(regex)
		res = r.findall(text)
		if res :
			return res
		return []
	@staticmethod
	def check_match(regex,text):
		r = re.compile(regex)
		return r.match(text)
	@staticmethod
	def replace_all(regex,replace,text):
		return re.sub(regex,replace,text)
	@staticmethod
	def all_groups(regex,text):
		r = re.match(regex,text)
		if r:
			return r.groups()
		return []
		
