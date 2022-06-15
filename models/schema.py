import graphene
#from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType

import lib.db.graphene.types as t

from lib.db.graphene.util import UtilGraphene
from models.models import Department as DepartmentModel
from models.models  import Employee as EmployeeModel
from models.models  import Role as RoleModel

class Department(MongoengineObjectType):
	class Meta:
		model = DepartmentModel
		#interfaces = (Node,)

class Role(MongoengineObjectType):
	class Meta:
		model = RoleModel
	# interfaces = (Node,)

class UpdateRole(graphene.Mutation):
	class Arguments:
		id = graphene.String()
		name = graphene.String()

	role = graphene.Field(lambda: Role)

	def mutate(root, info, **kwargs):
		print(kwargs)
		role = RoleModel.create_or_update(kwargs)
		return UpdateRole(role=role)

class Employee(MongoengineObjectType):

	class Meta:
		model = EmployeeModel
		#interfaces = (Node,)

class PaginableEmployeeType(t.PaginableType):
	items = graphene.List(Employee,source="items")

class Query(graphene.ObjectType):
	#node = Node.Field()
	all_employees = graphene.Field(PaginableEmployeeType,
		search=graphene.String(),
		skip=graphene.Int(),
		limit=graphene.Int())
	# all_role = MongoengineConnectionField(Role)
	role = graphene.Field(Role)

	def resolve_all_employees(parent, info,**kwargs):
		# We can easily optimize query count in the resolve method
		# user = info.context.user
		# if not user.is_authenticated:
		# 	raise Exception('You must be logged in')

		print("all_employees parent: %s"%parent)
		
		if 'search' in kwargs:
			kwargs['query'] = {
				"name":kwargs['search']
			}

		return UtilGraphene.as_paginable(EmployeeModel.all_employees(kwargs))
class Mutations(graphene.ObjectType):
	update_role = UpdateRole.Field()

#schema = graphene.Schema(query=Query, types=[Department, Employee, Role], mutation=Mutations)



