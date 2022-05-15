import graphene
#from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType

from lib.log.UtilLog import UtilLog
from lib.db.mongo.util import UtilMongoEngine


from lib.db.graphene.util import PaginableType,UtilGraphene
from lib.service.auth.db.mongoengine.models import Account as AccountModel, User as UserModel

###############################################################################
# Account
###############################################################################
# -- model map
class AccountType(MongoengineObjectType):
	class Meta:
		model = AccountModel
# -- model pagination
class AccountPaginableType(PaginableType):
	items = graphene.List(AccountType,source="items")
# -- mutation
class AccountCreateUpdate(graphene.Mutation):
	class Arguments:
		id = graphene.String()
		name = graphene.String()
		#accounts = graphene.List(graphene.String())

	account = graphene.Field(lambda: AccountType)

	def mutate(root, info, **kwargs):
		account = UtilMongoEngine.create_or_update(AccountModel,**kwargs)
		return AccountCreateUpdate(account=account)

###############################################################################
# User
###############################################################################
# -- model map
class UserType(MongoengineObjectType):
	class Meta:
		model = UserModel
# -- model pagination
class UserPaginableType(PaginableType):
	items = graphene.List(UserType,source="items")

# -- mutation
class UserCreateUpdate(graphene.Mutation):
	class Arguments:
		id = graphene.String()
		name = graphene.String()
		lastname = graphene.String()
		email = graphene.String()
		password = graphene.String()
		#accounts = graphene.List(graphene.String())

	user = graphene.Field(lambda: UserType)

	def mutate(root, info, **kwargs):
		print(kwargs)
		user = UserModel.user_create_or_update(kwargs)
		return UserCreateUpdate(user=user)



###############################################################################
# declare graphql query
###############################################################################
class Query(graphene.ObjectType):
	all_accounts = graphene.Field(AccountPaginableType,
			search=graphene.String(),
			skip=graphene.Int(),
			limit=graphene.Int()
		)
	all_users = graphene.Field(UserPaginableType,
			search=graphene.String(),
			skip=graphene.Int(),
			limit=graphene.Int()
		)
	@staticmethod
	def build_search_query(key,kwargs):
		if 'search' in kwargs:
			kwargs['query'] = {
				key:kwargs['search']
		}
	
	def resolve_all_accounts(parent, info,**kwargs):
		Query.build_search_query('name',kwargs)
		#return UtilGraphene.as_paginable(AccountModel.all_accounts(kwargs))
		return UtilGraphene.paginable_mongo(AccountModel,**kwargs)

	def resolve_all_users(self, info,**kwargs):
		Query.build_search_query('name',kwargs)
		#return UtilGraphene.as_paginable(UserModel.all_users(kwargs))
		return UtilGraphene.as_paginable(UtilMongoEngine.list_paginable(UserModel,kwargs))

###############################################################################
# declare graphql mutations
###############################################################################
class Mutations(graphene.ObjectType):
	account_create_or_update = AccountCreateUpdate.Field()
	user_create_or_update = UserCreateUpdate.Field()
