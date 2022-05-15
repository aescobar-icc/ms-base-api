from mongoengine.base import (
    BaseDocument,
)
from mongoengine import Document,EmbeddedDocument
from mongoengine.fields import (
	DateTimeField, ReferenceField,IntField, StringField,EmbeddedDocumentField,BooleanField,ListField,SequenceField
)
from mongoengine import signals



class BaseDoc(EmbeddedDocument):
	meta = {
		"allow_inheritance":True
	}
# -------------------------------------------
# account
# -------------------------------------------
class AccountBase(BaseDocument):
	accountType = StringField()
	name		= StringField(unique = True)
	active		= BooleanField(default=True)
	
class Account(AccountBase,Document):
	accountParent = ReferenceField('Account')
	
	meta = {
		'strict': False,
		'collection': 'accounts',
		'indexes': [
			('accountParent')
		]
	}


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
		'indexes': [
			('accounts')
		]
	}