from http.client import HTTPConnection,HTTPSConnection
import json

from lib.log.UtilLog import UtilLog
from lib.sys.SysEnv import SysEnv
from lib.exceptions.ExceptionApi import ExceptionApi

class ServiceMail:
    @staticmethod
    def sendMail(mail):
        
        if 'subject' not in mail or  not isinstance(mail['subject'],str):
            raise ExceptionApi(400,'mail.subject must be string')
        if 'recipients' not in mail or  not isinstance(mail['recipients'],list):
            raise ExceptionApi(400,'mail.recipients must be list')
        if 'body' not in mail or  not isinstance(mail['body'],str):
            raise ExceptionApi(400,'mail.body must be string')

        try:
            urlparts	= SysEnv.getUrl('MS_NOTIFY_MAIL')
            UtilLog.debug(urlparts)
            if urlparts['protocol'] == 'https' :
                conn    = HTTPSConnection(urlparts['host'])
            else:
                conn    = HTTPConnection(urlparts['host'])
                
            mail = json.dumps(mail)
            headers = {"Content-type": "application/json","Accept": "*/*"}

            conn.request("POST", urlparts['path']+'/send-mail', mail, headers)
            response = conn.getresponse()
            print(response.status, response.reason)

            data = response.read()
            print(data)

        except Exception as e:
            msg = 'Error sending mail: %s'%str(e)
            UtilLog.error(msg)
            raise ExceptionApi(500,msg)
        finally:
            if conn is not None:
                conn.close()