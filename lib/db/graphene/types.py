from graphene.types import Scalar
from graphql.language import ast
import json
import graphene as g

class PaginableType(g.ObjectType):
	count		= g.Int()
	items_count	= g.Int()
	page 		= g.Int()
	page_count	= g.Int()
	offset		= g.Int()
	limit		= g.Int()
	has_next 	= g.Boolean()

class JSON(Scalar):
	'''JSON structure'''
	
	@staticmethod
	def is_native(node):
		return isinstance(node, (ast.StringValue,ast.BooleanValue,ast.IntValue,ast.FloatValue))
	@staticmethod
	def parse_native(node):
		if isinstance(node, ast.StringValue):
			return node.value
		if isinstance(node, ast.BooleanValue):
			return bool(node.value)
		if isinstance(node, ast.IntValue):
			return int(node.value)
		if isinstance(node, ast.FloatValue):
			return float(node.value)

		raise Exception('JSON parse_native error for node: %s' % node)
	@staticmethod
	def parse_obj(node):
		#print('JSON parse_obj', node)
		if isinstance(node, ast.ObjectValue):
			obj = {}
			for field in node.fields:
				obj[field.name.value] = JSON.parse_obj(field.value)
			return obj
		if isinstance(node, ast.ListValue):
			return [JSON.parse_obj(v) for v in node.values  ]
		if JSON.is_native(node):
			return JSON.parse_native(node)
		else:
			print('JSON parse_obj unknow!!', node)
			return None
	
	##################################################
	### GraphQL Base Implementation 
	##################################################
	@staticmethod
	def serialize(dt):
		print('JSON serialize', dt)
		return json.dumps(dt)
	@staticmethod
	def parse_literal(node):
		#print('JSON parse_literal', node)
		return JSON.parse_obj(node)
	@staticmethod
	def parse_value(value):
		print('JSON parse_value', value)
		return json.loads(value)