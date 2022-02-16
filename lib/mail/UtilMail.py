import hashlib
import os.path
import traceback
import smtplib, ssl

from lib.log.UtilLog import UtilLog
from lib.sys.SysEnv import SysEnv
from lib.parser.UtilParser import UtilParser
from lib.service.UtilService import UtilService


class UtilMail:
    need_mail	= SysEnv.get('MAIL_SERVER',False)

    #deprecated
    @staticmethod
    def initMail(app):
        pass
    @staticmethod
    def sendMail(msg):
        if not UtilMail.need_mail:
            UtilLog.error('to send mail config env is required.')
            return

        hash_object = hashlib.md5(repr(msg).encode('utf-8')).hexdigest()

        if os.path.isfile('/tmp/%s'%hash_object):
            UtilLog.debug('mail %s it`s already been sent'%hash_object)
            return
        f = open('/tmp/%s'%hash_object,'w+')
        f.write('0')
        f.close()


        if 'sender' not in msg or msg['sender'] == '':
            msg['sender'] = SysEnv.get('MAIL_USERNAME')
        if 'subject' not in msg or msg['subject'] == '':
            msg['subject'] = 'UtilMail Service Message'
        try:
            #m = Message(msg['subject'], sender = msg['sender'], recipients = msg['recipients'])
            #m.body = msg['body']
            #UtilMail.mail.send(m)

            MAIL_SERVER   = SysEnv.get('MAIL_SERVER')
            MAIL_PORT     = SysEnv.get('MAIL_PORT',465,int)
            MAIL_USERNAME = SysEnv.get('MAIL_USERNAME')
            MAIL_PASSWORD = SysEnv.get('MAIL_PASSWORD')
            MAIL_USE_TLS  = SysEnv.get('MAIL_USE_TLS',False,UtilParser.str2bool)
            MAIL_USE_SSL  = SysEnv.get('MAIL_USE_SSL',True,UtilParser.str2bool)

            
            recipients = SysEnv.get('MAIL_RECIPIENTS').split(',')

            message = 'From: "Mail Notifier"<{}>\nSubject: {}\n\n{}'.format(MAIL_USERNAME,msg['subject'], msg['body'])

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, context=context) as server:
                #server.set_debuglevel(1)
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.sendmail(MAIL_USERNAME, recipients, message)

            #UtilLog.debug('sending mail:')
            #UtilLog.debug('%s'%hash_object)
            #UtilLog.debug('%s'%msg)
        except Exception as e:
            UtilLog.error('Error sending Error-Mail:%s'%str(e))
            #traceback.print_exc()
            os.remove('/tmp/%s'%hash_object)

    @staticmethod
    def sendError(request,msg):
        hash_object = hashlib.md5(repr(msg).encode('utf-8')).hexdigest()

        if os.path.isfile('/tmp/%s'%hash_object):
            UtilLog.debug('mail %s it`s already been sent'%hash_object)
            return
        f = open('/tmp/%s'%hash_object,'w+')
        f.write('0')
        f.close()

        msg = '%s\nSERVER ERROR:\n%s'%(UtilService.getServiceInfo(request),msg )

        podName = SysEnv.get('MY_POD_NAME','unknow pod')
        recipients = SysEnv.get('MAIL_RECIPIENTS').split(',')
        UtilMail.sendMail({ 'subject':'Assurance Error - '+podName, 
                            'body':msg, 
                            'recipients':recipients
                        })
