from lib.log.UtilLog import UtilLog

import traceback

class ExceptionApi(Exception):
    status_code=500
    message="server internal error"
    excepData=None
    def __init__(self, status_code,message,error_code="N/A",exceptionData=None):
        self.status_code=status_code
        self.message=message
        self.error_code = error_code
        self.exceptionData = exceptionData

    @staticmethod
    def raiseError(msg):
        UtilLog.error(msg)
        traceback.print_exc()
        raise ExceptionApi(500,msg)