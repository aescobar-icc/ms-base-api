
from lib.regex.UtilRegex import UtilRegex
from urllib.parse import quote
class UtilUrl:

	@staticmethod
	def getUrlParts(url):
		if not url.endswith('/') and '?' not in url:
			url = url +'/'
		urlRegx = r'(https?):\/\/((.*?)(:(\d*))?)(\/.*)'
		groups = UtilRegex.all_groups(urlRegx,url)

		if len(groups) == 0:
			raise Exception(' %s  is not valid url'%(url))

		return {
			'protocol':groups[0],
			'host':groups[1],
			'hostname':groups[2],
			'port':groups[4],
			'path':groups[5]
		}
	@staticmethod
	def get_dict(names,regex,url):
		d = {}
		try:
			iq = url.index("?")
			query = url[iq+1:]
			url = url[0:iq]
			query = query.split("&")
			for kv in query:
				kv = kv.split("=")
				if len(kv) == 2:
					d[kv[0]] = kv[1]
				else:
					d[kv[0]] = None
		except:
			pass


		values = list(UtilRegex.all_groups(regex,url))
		for i,n in enumerate(names):
			d[n] = values[i]
		return d
	@staticmethod
	def encodeURIComponent(str):
		return quote(str.encode("utf-8"))
	@staticmethod
	def create_query(data,only=None):
		encode = UtilUrl.encodeURIComponent
		q ="?"
		if only is None:
			for key, value in data.items():
				q += "%s=%s&"%(encode(key),encode(value))
		else:
			for key in only:
				q += "%s=%s&"%(encode(key),encode(data[key]))
		return q