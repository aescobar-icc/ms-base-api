## ##############################################################
## @author: Adán Escobar
## @mail: aescobar.icc@gmail.com
## ##############################################################

import logging
import sys
import os
import traceback
import re

from lib.regex.UtilRegex import UtilRegex

class UtilLog:
    Red='\033[0;31m'
    Green='\033[0;32m' 
    BrownOrange='\033[0;33m'
    Blue='\033[0;34m' 
    Purple='\033[1;35m'
    NoColor='\033[0m' # No Color

    ready = False
    LOGGER = None
    #this is called from app
    @staticmethod
    def initLog(name='gunicorn.error'):
        if UtilLog.ready :
            return
        #only use gunicorn.error logger for all logging
        if name is not None:
            UtilLog.LOGGER = logging.getLogger(name)
            UtilLog.LOGGER.setLevel(os.environ.get('DEBUG_LEVEL','INFO'))
        else:
            logging.basicConfig(level=os.environ.get('DEBUG_LEVEL','INFO'))
            UtilLog.LOGGER = logging
        UtilLog.LOGGER.debug('[AE.LIB][UtilLog] initialized.')
        
        #sys.stderr = UtilLog
        sys.stdout = UtilLog

        UtilLog.ready = True

    def write(msg) :
        if not UtilLog.ready :
            UtilLog.initLog()
        if msg != "" and  msg != "\n":
            UtilLog.LOGGER.info('%s %s'%(UtilLog.get_caller(),msg))
    
    def flush():
        pass

    @staticmethod
    def info(msg, *args, **kwargs):
        if not UtilLog.ready :
            UtilLog.initLog()
        UtilLog.LOGGER.info('%s %s %s %s %s'%(UtilLog.Purple,UtilLog.get_caller(),UtilLog.Green,msg,UtilLog.NoColor))
    @staticmethod
    def warning(msg, *args, **kwargs):
        if not UtilLog.ready :
            UtilLog.initLog()
        UtilLog.LOGGER.warning('%s %s %s %s %s'%(UtilLog.Purple,UtilLog.get_caller(),UtilLog.BrownOrange,msg,UtilLog.NoColor))
    @staticmethod
    def debug(msg, *args, **kwargs):
        if not UtilLog.ready :
            UtilLog.initLog()
        UtilLog.LOGGER.debug('%s %s %s %s %s'%(UtilLog.Purple,UtilLog.get_caller(),UtilLog.Blue,msg,UtilLog.NoColor))
    @staticmethod
    def error(msg, *args, **kwargs):
        if not UtilLog.ready :
            UtilLog.initLog()
        UtilLog.LOGGER.error('%s %s %s %s %s'%(UtilLog.Purple,UtilLog.get_caller(),UtilLog.Red,msg,UtilLog.NoColor))

    @staticmethod
    def get_caller():
        stack = traceback.format_stack()
        groups = UtilRegex.all_groups('\s+File\s+"(.*?)",\s+line\s+(\d+),\s+in\s+(.*?)\n',stack[-3])
        callerFile = re.sub('((.*?)\/)+(.*)\.py',r'\3',groups[0]) 
        callerLine = groups[1]
        callerFunc = groups[2]
        return '[%s.%s(%s)]'%(callerFile,callerFunc,callerLine)

