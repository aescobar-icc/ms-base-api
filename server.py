from flask import request

from flask_graphql import GraphQLView

from lib.server.ServerApi import ServerApi
from lib.db.mongo.connection import MongoConnection
import schema

app = ServerApi.init()
MongoConnection.connect(app)

#enable GraphiQL
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema.schema, graphiql=True)
)
	
@app.before_request
def before_request_api():
	ServerApi.before_request(request)

@app.after_request
def after_request_api(response):
	return ServerApi.after_request(response)

@app.errorhandler(Exception)
def errorhandler(error):
	return ServerApi.errorhandler(error)

