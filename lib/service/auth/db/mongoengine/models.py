from mongoengine.base import (
    BaseDocument,
)
from mongoengine import Document,EmbeddedDocument
from mongoengine.fields import (
	DateTimeField, ReferenceField,IntField, StringField,EmbeddedDocumentField,BooleanField,ListField,SequenceField,
	EnumField
)
from mongoengine import signals
from enum import Enum,IntEnum

from lib.enum.util import UtilEnum
from lib.db.mongo.util import UtilMongoEngine



class BaseDoc(EmbeddedDocument):
	meta = {
		"allow_inheritance":True
	}
# -------------------------------------------
# AccountType
# -------------------------------------------
class ACCOUNT_TYPE(str,Enum):
	PUBLIC=('public',[])
	PROVIDER=('provider',['public'])
	CUSTOMER=('customer',['public','provider'])
	MASTER=('master',None)

	#def __init__(self,value,can_create) -> Enum:
	def __new__(cls, value,can_create):
		obj = str.__new__(cls, [value])
		obj._value_=value
		obj.can_create=can_create
		return obj

	def need_parent(self):
		if self==ACCOUNT_TYPE.MASTER:
			return False
		return True
		
	def can_create(self,child_type:Enum) -> bool:
		return child_type in self.can_create
class AccountType(EmbeddedDocument):
	type = EnumField(ACCOUNT_TYPE,required=True) # master, customer, provider, public
	# meta = {
	# 	'strict': False,
	# 	'collection': 'accounts_types',
		
	# }

# -------------------------------------------
# account
# -------------------------------------------
class AccountBase(BaseDocument):
	#accountType = EmbeddedDocumentField(AccountType,required=True)
	#type = EnumField(ACCOUNT_TYPE,required=True) # master, customer, provider, public

	name		= StringField()
	type		= StringField(required = True)
	active		= BooleanField(default=True)
class AccountSummary(AccountBase,EmbeddedDocument):
	id		= StringField()
	
UtilMongoEngine.create_init(AccountSummary)
class Account(AccountBase,Document):
	name		= StringField(unique = True)
	accountParent = ReferenceField('Account')
	accountParentSummary = EmbeddedDocumentField(AccountSummary)
	
	meta = {
		'strict': False,
		'collection': 'accounts',
		# 'indexes': [
		# 	('accountParent')
		# ]
	}
	def __str__(self): 
		return "[Account] id:%s, name:%s"%(self.id,self.name)
	@staticmethod
	def pre_save(sender, document):
		print("[debug] Account.pre_save")
		#validate account type
		
		#UtilEnum.validate(ACCOUNT_TYPE,{"Account.type":document.type})

		if document.id is not None:
			document.type =	Account.objects.get(id=document.id).type

		enum = UtilEnum.get_by_value(ACCOUNT_TYPE,document.type)
		if enum is None:
			raise Exception("Account.type='%s' is not present in enum %s with values=%s "%(document.type,UtilEnum.values(ACCOUNT_TYPE)))

		#validate account parent
		if enum.need_parent() and not document.accountParent:

			raise Exception("Account.accountParent is required")

		#print("accountParent1:",document.accountParent)
		#parent = Account.objects.get(id=document.accountParent.id)
		print("[debug] accountParent2:",document.accountParent)
		#document.accountParentSummary = AccountSummary(UtilMongoEngine.adapt_kwargs(AccountSummary,**document.accountParent.to_mongo()))
		sumDict = UtilMongoEngine.to_dict(document.accountParent)

		print("[debug] sumDict:",sumDict)
		document.accountParentSummary = AccountSummary(**sumDict)
		# if document.accountParent.type.type not in document.type.can_create:
		# 	raise Exception("Account.type can not be created by Account.accountParent.type")


signals.pre_save.connect(Account.pre_save, sender=Account)

# -------------------------------------------
# user
# -------------------------------------------
class UserBase(BaseDocument):
	email		= StringField(required = True)
	password	= StringField(required = True)
	active		= BooleanField(default = True)
	#accounts_summary  = ListField(AccountBase)

class User(Document,UserBase):
	accounts = ListField(ReferenceField(Account))

	meta = {
		'strict': False,
		'collection': 'users',
		# 'indexes': [
		# 	('accounts')
		# ]
	}