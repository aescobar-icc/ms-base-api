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
###############################################################################
# AccountType
###############################################################################
class ACCOUNT_TYPE(str,Enum):
	PUBLIC=('public',[])
	PROVIDER=('provider',['public'])
	CUSTOMER=('customer',['public','provider'])
	MASTER=('master',None)

	#def __init__(self,value,can_create) -> Enum:
	def __new__(cls, value,allow_to_create):
		obj = str.__new__(cls, [value])
		obj._value_=value
		obj.allow_to_create=allow_to_create
		return obj

	def need_parent(self):
		if self==ACCOUNT_TYPE.MASTER:
			return False
		return True
		
	def can_create(self,child_type:Enum) -> bool:
		if self==ACCOUNT_TYPE.MASTER:
			return True
		return child_type._value_ in self.allow_to_create
class AccountType(EmbeddedDocument):
	type = EnumField(ACCOUNT_TYPE,required=True) # master, customer, provider, public
	# meta = {
	# 	'strict': False,
	# 	'collection': 'accounts_types',
		
	# }

###############################################################################
# account
###############################################################################
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
	_accountParentSummary = EmbeddedDocumentField(AccountSummary,db_field="accountParentSummary")

	#-------------------------------------------------------------------------
	# accountParentSummary getter/setter definition
	#-------------------------------------------------------------------------
	def get_accountParentSummary(self):
		return self._accountParentSummary
	def set_accountParentSummary(self, value):
		if value is None or isinstance(value, AccountSummary):
			self._accountParentSummary = value
		elif isinstance(value, Account):
			self._accountParentSummary = AccountSummary(**UtilMongoEngine.to_dict(value))
		elif isinstance(value, dict):
			self._accountParentSummary = AccountSummary(**value)
		else:
			self._accountParentSummary = None
	accountParentSummary = property(get_accountParentSummary, set_accountParentSummary,)
	#-------------------------------------------------------------------------
	
	meta = {
		'strict': False,
		'collection': 'accounts',
		# 'indexes': [
		# 	('accountParent')
		# ]
	}
	def __str__(self): 
		return "[Account] id:%s, name:%s, type:%s"%(self.id,self.name,self.type)
	@staticmethod
	def pre_save(sender, document):
		account=document
		print("[debug] Account.pre_save")
		#validate account type
		
		#UtilEnum.validate(ACCOUNT_TYPE,{"Account.type":document.type})

		if account.id is not None:
			bd_doc = Account.objects.get(id=account.id)
			account.type 			=	bd_doc.type
			account.accountParent	=	bd_doc.accountParent

		accountType = UtilEnum.get_by_value(ACCOUNT_TYPE,account.type)
		if accountType is None:
			raise Exception("Account.type='%s' is not present in enum ACCOUNT_TYPE with values=%s "%(account.type,UtilEnum.values(ACCOUNT_TYPE)))

		#validate account parent
		if accountType.need_parent() and not account.accountParent:
			raise Exception("Account.accountParent is required")

		print("[debug] accountParent2:",account.accountParent)
		#it is safe set accountParentSummary with accountParent because accountParentSummary is a property that process de value before assign
		account.accountParentSummary = account.accountParent
		if account.accountParent is not None:
			parentType = UtilEnum.get_by_value(ACCOUNT_TYPE,account.accountParent.type)
			print("[debug] parentType:",parentType)
			if parentType.can_create(accountType):
				print("[debug] accountParent:",account.accountParent)
				account.accountParent = account.accountParent.id
			else:
				raise Exception("Account.accountParent.type=%s can not create Account.type='%s' "%(account.accountParent.type,account.type))

	@staticmethod
	def post_save(sender, document,created):
		account=document
		#UtilLog.debug("sender:%s, account:%s"%(sender,account))
		all_account_childs = Account.objects(accountParent=account)
		
		#update sumary info of all account childs
		for e in all_account_childs:
			e.accountParentSummary = AccountSummary(**UtilMongoEngine.to_dict(account))
			e.save()


signals.pre_save.connect(Account.pre_save, sender=Account)
signals.post_save.connect(Account.post_save, sender=Account)

###############################################################################
# user
###############################################################################
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