from flask import Flask, request, Response, jsonify
from lib.util import check_essential_env
from jwcrypto import jwt, jwk, jws
from lib.mongo import db
from lib.config import config
import json
import bcrypt
import time
import random

# Essential Instances
app = Flask(__name__)


# @status: Done, not yet tested
@app.route('/assets')
def assets():
    asset = '/html/%s' % request.values.get('file')

    # Basic security check
    if os.path.commonprefix((os.path.realpath(asset), '/html/')) != '/html/':
        return Response('Asset not found.', mimetype='text/plain'), 404

    with open('/html/%s' % asset) as asset_file:

        # Returns JS
        if asset.endswith('.js'):
            return Response(asset_file.read(), mimetype='application/javascript'), 200

        # Returns CSS
        if asset.endswith('.css'):
            return Response(asset_file.read(), mimetype='text/css'), 200

    # Asset not found
    return Response('Asset not found.', mimetype='text/plain'), 404


# @status: Under development
@app.route('/', methods=['GET'])
def setup():

    # Check all essential environment variable
    if check_essential_env():

        # Perform re-setup.
        return ''

    # Do nothing
    return ''


# @status: Under development
@app.route('/', methods=['POST'])
def set_environment():

    # Check all essential environment variable
    if check_essential_env():

        # Set environment set from Qq
        return ''

    return ''

#
# @app.route('/login', methods=['POST'])
# def login():
#     auto_create_default_user()
#     user = db()['users'].find_one({"username": request.values.get('username').lower()})
#     valid_username = request.values.get('username').lower() == user['username'].lower()
#     valid_password = bcrypt.hashpw(request.values.get('password').encode('utf-8'), user['password']) == user['password']
#
#     if valid_username and valid_password:
#         token = jwt.JWT(header={'alg': 'HS256'}, claims={
#             'usr': user['username'],
#             'iat': int(time.time()),
#             'exp': int(time.time() + 900)
#         })
#         token.make_signed_token(jwk.JWK.from_json(json.dumps(config()['auth']['jwk'])))
#         return Response(json.dumps({"msg": "Login success.", "jws": token.serialize()}), mimetype='application/json'), 200
#     return Response(json.dumps({"msg": "Invalid username and/or password"}), mimetype='application/json'), 403
#
#
# @app.route('/login-agent', methods=['POST'])
# def login_agent():
#     auto_create_default_agent()
#     query = {"name": request.values.get('name').lower()}
#     agent = db()['agents'].find_one(query)
#
#     if agent and bcrypt.hashpw(request.values.get('password').encode('utf-8'), agent['password']) == agent['password']:
#         new_password = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for i in range(32)).encode('utf-8')
#         db()['agents'].update_one(query, {"$set": {"password": bcrypt.hashpw(new_password, bcrypt.gensalt())}})
#         token = jwt.JWT(header={'alg': 'HS256'}, claims={
#             'usr': agent['name'],
#             'iat': int(time.time()),
#             'exp': int(time.time() + 900)
#         })
#         token.make_signed_token(jwk.JWK.from_json(json.dumps(config()['auth']['jwk'])))
#         return Response(json.dumps({"msg": "Agent connected successfully.", "jws": token.serialize(), "new_password": new_password.decode('utf-8')}), mimetype='application/json'), 200
#     return Response(json.dumps({"msg": "Invalid agent credentials"}), mimetype='application/json'), 403
#
#
# @app.route('/assets/agent.py', methods=['GET'])
# def download_agent():
#     with open('asset/agent.py', 'r') as agent_file:
#         return Response(agent_file.read(), mimetype='application/octet-stream'), 200
#
#
# @app.route('/verify', methods=['GET'])
# def verify_token():
#     try:
#         jwt.JWT(jwt=request.headers.get('Authorization')[7:], key=jwk.JWK.from_json(json.dumps(config()['auth']['jwk'])))
#         return Response('{"msg":"Token is valid"}', mimetype='application/json'), 200
#     except jws.InvalidJWSSignature:
#         return Response('{"msg":"Token is invalid"}', mimetype='application/json'), 403
#
#
# @app.errorhandler(404)
# def error_404(e):
#     return Response('{"msg": "Error 404. Resource not found."}', mimetype='application/json'), 404
#
#
# def auto_create_default_user():
#     default_user = db()['users'].find_one({"username": "ghabxph"})
#     if not default_user:
#         db()['users'].insert_one({"username": "ghabxph", "password": bcrypt.hashpw(b'stonkestpw', bcrypt.gensalt())})
#
#
# def auto_create_default_agent():
#     default_agent = db()['agents'].find_one({"name": "first-agent"})
#     if not default_agent:
#         db()['agents'].insert_one({"name": "first-agent", "password": bcrypt.hashpw(b'stonkestpw', bcrypt.gensalt())})