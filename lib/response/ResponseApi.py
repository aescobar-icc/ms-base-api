from flask import Response

class ResponseApi(Response):
    default_mimetype = 'application/json'