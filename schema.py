import graphene as g
from lib.service.auth.db.mongoengine.schema import Query as AuthQuery, Mutations as AuthMutation
from models.schema import Query as ApiQuery, Mutations as ApiMutation

class Query(AuthQuery,ApiQuery, g.ObjectType):
	pass
class Mutation(AuthMutation, ApiMutation, g.ObjectType):
	pass

schema = g.Schema(query=Query,mutation=Mutation,auto_camelcase=False)
