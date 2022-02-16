
from codecs import encode

from http.client import HTTPConnection,HTTPSConnection
from lib.log.UtilLog import UtilLog
from lib.sys.SysEnv import SysEnv

from lib.exceptions.ExceptionApi import ExceptionApi
from lib.url.UtilUrl import UtilUrl

import json
import traceback
class UtilHttp:

	def get_connection(urlparts):
		UtilLog.debug(urlparts)
		if urlparts['protocol'] == 'https' :
			conn    = HTTPSConnection(urlparts['host'])
		else:
			conn    = HTTPConnection(urlparts['host'])
		return conn

	@staticmethod
	def build_form_data(params,boundary):
		dataList = []

		for k in params: 
			dataList.append(encode('--' + boundary))
			dataList.append(encode('Content-Disposition: form-data; name=%s;'%k))
			dataList.append(encode('Content-Type: text/plain'))
			dataList.append(encode(''))
			dataList.append(encode(params[k]))
			dataList.append(encode('--' + boundary))
		dataList.append(encode(''))
		payload = b'\r\n'.join(dataList)
		return payload

	@staticmethod
	def call_api(data,parseJson=True):
		resp_data = None
		try:
			if "url" not in data:
				raise ExceptionApi(400,"[call_api] data['url'] is required")
			if "method" not in data:
				raise ExceptionApi(400,"[call_api] data['method'] is required")

			in_data   	= {} if "requestBody" not in data else json.dumps(data["requestBody"])
			query		= "" if "requestQuery" not in data else UtilUrl.create_query(data["requestQuery"])
			headers 	= {"Content-type": "application/json","Accept": "*/*"} if not "headers" in data else data["headers"]

			urlparts    = UtilUrl.getUrlParts(data["url"])
			conn        = UtilHttp.get_connection(urlparts)
			path = urlparts['path'] 
			if query != "":
				if path.endswith("/"):
					path = path[:-1]
				path += query
            
			#UtilLog.warning("%s"%(path))
			conn.request(data["method"],path, in_data, headers)
			response = conn.getresponse()
			if response.status >= 300:
				UtilLog.debug(response.status, response.reason)
			
			resp_data = response.read().decode("utf-8")
			if response.status >= 300:
				UtilLog.debug(resp_data)
				resp_data = {
					"request_data":data,
					"response_status": response.status,
					"response_data":resp_data
				}
			elif parseJson:
				resp_data = json.loads(resp_data)

		except Exception as e:
			UtilLog.error("Error parsing json: %s EXC:%s"%(resp_data, e))
			traceback.print_exc()
			#raise ExceptionApi(400,"%s"%e)
			resp_data = {
				"request_data":data,
				"response_status": response.status,
				"response_data":resp_data
			}
			
		return resp_data
