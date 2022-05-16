from urllib import response
from graphene.test import Client
import schema

from lib.service.auth.db.mongoengine.models import Account,ACCOUNT_TYPE
from lib.enum.util import UtilEnum

class AccountTest:
	#mutations
	account_create_or_update = '''
					mutation account_create_or_update {
						account_create_or_update(%s) {
							account {
								name
							}
						}
					}
				'''
	
	def account_create_or_update_response(account_name):
		return { "data": { "account_create_or_update": { "account": { "name": account_name } } } }


	@staticmethod
	def account_1_master_test():
		print("[test] 1.- testing create master account")
		client = Client(schema.schema)
		account_name = "account 1"
		args='name: "%s",type:"master"'%account_name
		executed = client.execute(AccountTest.account_create_or_update%args)
		assert executed == AccountTest.account_create_or_update_response(account_name)


	@staticmethod
	def account_2_customer_test():
		print("[test] 2.- testing create customer account")
		client = Client(schema.schema)
		account_name = "account 2 - customer"
		parentId = Account.objects.get(name="account 1").id
		args='name: "%s",type:"customer" accountParent:"%s"'%(account_name,parentId)
		executed = client.execute(AccountTest.account_create_or_update%args)
		assert executed == AccountTest.account_create_or_update_response(account_name)

	@staticmethod
	def account_3_provider_test():
		print("[test] 3.- testing create provider account")
		client = Client(schema.schema)
		account_name = "account 3 - provider"
		parentId = Account.objects.get(name="account 2 - customer").id
		args='name: "%s",type:"provider" accountParent:"%s"'%(account_name,parentId)
		executed = client.execute(AccountTest.account_create_or_update%args)
		assert executed == AccountTest.account_create_or_update_response(account_name)
	@staticmethod
	def account_4_public_test():
		print("[test] 4.- testing create public account")
		client = Client(schema.schema)
		account_name = "account 4 - public"
		parentId = Account.objects.get(name="account 2 - customer").id
		args='name: "%s",type:"public" accountParent:"%s"'%(account_name,parentId)
		executed = client.execute(AccountTest.account_create_or_update%args)
		assert executed == AccountTest.account_create_or_update_response(account_name)
	@staticmethod
	def account_5_change_name_test():
		print("[test] 5.- testing change name account: 'account 2 - customer'")
		client = Client(schema.schema)
		account_name = "account 2 - customer - changed"
		parentId = Account.objects.get(name="account 2 - customer").id
		args='id:"%s",name:"%s"'%(parentId,account_name)
		executed = client.execute(AccountTest.account_create_or_update%args)
		print(executed)
		assert executed == AccountTest.account_create_or_update_response(account_name)

	@staticmethod
	def account_6_invalid_type_test():
		print("[test] 6.- testing try create account with invalid type")
		client = Client(schema.schema)
		type="invalid_test_type"
		args='name: "account test",type:"%s"'%type
		executed = client.execute(AccountTest.account_create_or_update%args)
		msg=executed["errors"][0]["message"]
		print(msg)
		assert msg == "Account.type='%s' is not present in enum ACCOUNT_TYPE with values=%s "%(type,UtilEnum.values(ACCOUNT_TYPE))
	
	@staticmethod
	def account_7_no_parent_test():
		print("[test] 7.- testing try create account without parent")
		client = Client(schema.schema)
		type="customer"
		args='name: "account test",type:"%s"'%type
		executed = client.execute(AccountTest.account_create_or_update%args)
		msg=executed["errors"][0]["message"]
		print(msg)
		assert msg == "Account.accountParent is required"

	@staticmethod
	def account_8_no_valid_parent_test():
		print("[test] 8.- testing try create account with invalid parent")
		client = Client(schema.schema)
		acc = Account.objects.get(name="account 4 - public")
		type="customer"
		args='name: "account test",type:"%s",accountParent:"%s" '%(type,acc.id)
		executed = client.execute(AccountTest.account_create_or_update%args)
		msg=executed["errors"][0]["message"]
		print(msg)
		assert msg == "Account.accountParent.type=%s can not create Account.type='%s' "%(acc.type,type)