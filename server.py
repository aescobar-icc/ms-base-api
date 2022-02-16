from flask import request

from lib.server.ServerApi import ServerApi

app = ServerApi.init()
	
@app.before_request
def before_request_api():
	ServerApi.before_request(request)

@app.after_request
def after_request_api(response):
	return ServerApi.after_request(response)

@app.errorhandler(Exception)
def errorhandler(error):
	return ServerApi.errorhandler(error)