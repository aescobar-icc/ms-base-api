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
	_accountParentSummary = EmbeddedDocumentField(AccountSummary,db_field="accountParentSummary")

	def get_accountParentSummary(self):
		print("getter method called")
		return self._accountParentSummary
	
	# function to set value of _age
	def set_accountParentSummary(self, value):
		print("setter method called")
		if value is None or isinstance(value, AccountSummary):
			self._accountParentSummary = value
		elif isinstance(value, Account):
			self._accountParentSummary = AccountSummary(**UtilMongoEngine.to_dict(value))
		elif isinstance(value, dict):
			self._accountParentSummary = AccountSummary(**value)
		else:
			self._accountParentSummary = None
	
	accountParentSummary = property(get_accountParentSummary, set_accountParentSummary,) 
	
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
			bd_doc = Account.objects.get(id=document.id)
			document.type 			=	bd_doc.type
			document.accountParent	=	bd_doc.accountParent

		enum = UtilEnum.get_by_value(ACCOUNT_TYPE,document.type)
		if enum is None:
			raise Exception("Account.type='%s' is not present in enum %s with values=%s "%(document.type,UtilEnum.values(ACCOUNT_TYPE)))

		#validate account parent
		if enum.need_parent() and not document.accountParent:
			raise Exception("Account.accountParent is required")

		print("[debug] accountParent2:",document.accountParent)
		#it is safe set accountParentSummary with accountParent because accountParentSummary is a property that process de value before assign
		document.accountParentSummary = document.accountParent
		# if document.accountParent.type.type not in document.type.can_create:
		# 	raise Exception("Account.type can not be created by Account.accountParent.type")

	@staticmethod
	def post_save(sender, document,created):
		#UtilLog.debug("sender:%s, document:%s"%(sender,document))
		all_account_childs = Account.objects(accountParent=document)
		
		#update sumary info of all account childs
		for e in all_account_childs:
			e.accountParentSummary = AccountSummary(**UtilMongoEngine.to_dict(document))
			e.save()


signals.pre_save.connect(Account.pre_save, sender=Account)
signals.post_save.connect(Account.post_save, sender=Account)

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