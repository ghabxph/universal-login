from flask import Flask
from flask import Response
from flask import request
from flask import redirect
from flask import jsonify
from lib.util import essential_env_present
from pymongo import MongoClient as mongo_client
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure
from requests.exceptions import ConnectionError
from jwcrypto import jwt, jwk, jws
# from lib.config import config
import os
import json
import random
import requests
import bcrypt
import time
import sys

# Essential Instances
app = Flask(__name__)


@app.route('/assets')
def assets():
    asset = '/html/%s' % request.values.get('file')

    # Basic security check
    if os.path.commonprefix((os.path.realpath(asset), '/html/')) != '/html/':
        return Response('Asset not found.', mimetype='text/plain'), 404

    with open(asset) as asset_file:

        # Returns JS
        if asset.endswith('.js'):
            return Response(asset_file.read(), mimetype='application/javascript'), 200

        # Returns CSS
        if asset.endswith('.css'):
            return Response(asset_file.read(), mimetype='text/css'), 200

    # Asset not found
    return Response('Asset not found.', mimetype='text/plain'), 404


@app.route('/', methods=['GET'])
def setup():

    with open('/html/setup.html', 'r') as html_file:

        # index.html file
        html = html_file.read()

        # Check all essential environment variable
        if essential_env_present():

            # Perform URL redirection (to /login)
            return redirect('/login')

        # Perform re-setup.
        return Response(html), 200


# @status: Under development
@app.route('/', methods=['POST'])
def set_environment():

    # Check all essential environment variable
    if essential_env_present():

        # Do nothing..
        return ''

    essential_env = {
        "UL_DB_HOST": request.values.get('UL_DB_HOST'),
        "UL_DB_ROOT_USER": request.values.get('UL_DB_ROOT_USER'),
        "UL_DB_ROOT_PASS": request.values.get('UL_DB_ROOT_PASS'),
        "UL_DB_NAME_PREFIX": request.values.get('UL_DB_NAME_PREFIX'),
        "UL_TP_CHECK": request.values.get('UL_TP_CHECK'),
        "UL_TP_URL": request.values.get('UL_TP_URL'),
        "UL_TP_REQUEST_FORMAT": request.values.get('UL_TP_REQUEST_FORMAT')
    }

    # Sets essential env setting
    for key in essential_env:
        if essential_env[key] is None:
            os.environ[key] = ''
        else:
            os.environ[key] = essential_env[key]

    # Set environment from submitted form
    return 'Environment setup is done!'


@app.route('/setup/verify/mongodb', methods=['POST'])
def setup_verify_mongodb():
    client = mongo_client(host=request.values.get('UL_DB_HOST'), serverSelectionTimeoutMS=5000)
    try:
        return Response(json.dumps({
            "type": "success",
            "msg": "Connection to mongodb host is successful.",
            "server_info": client.server_info()
        }, indent=4), mimetype='application/json'), 200
    except ServerSelectionTimeoutError:
        return Response('{"type":"error", "msg":"Unable to connect to mongodb host. Are you sure that the hostname is reachable?"}', mimetype='application/json'), 403


@app.route('/setup/verify/mongodb_admin_user', methods=['POST'])
def setup_verify_mongodbadminuser():
    client = mongo_client(
        host=request.values.get('UL_DB_HOST'),
        username=request.values.get('UL_DB_ROOT_USER'),
        password=request.values.get('UL_DB_ROOT_PASS'),
        serverSelectionTimeoutMS=500
    )
    try:
        return Response(json.dumps({
            "type": "success",
            "msg": "Test list_database operation is successful.",
            "list_databases": client.list_database_names()
        }), mimetype="application/json"), 200
    except OperationFailure:
        return Response(json.dumps({
            "type": "error",
            "msg": "MongoDB username and/or password may be invalid. Unable to perform list_database_names operation."
        }), mimetype='application/json'), 403


@app.route('/setup/verify/mongodb_admin_power', methods=['POST'])
def setup_verify_mongodbadminpower():
    client = mongo_client(
        host='svc-nosql',
        serverSelectionTimeoutMS=500
    )
    try:
        client.admin.authenticate(name=request.values.get('UL_DB_ROOT_USER'), password=request.values.get('UL_DB_ROOT_PASS'))
        return Response(json.dumps({
            "type": "success",
            "msg": "rolesInfo command succeed. We assume that user has root priviledge.",
            "rolesInfo": client.admin.command({
                'rolesInfo': {'role': 'root', 'db': 'admin'},
                'showPrivileges': True, 'showBuiltinRoles': True
            })}), mimetype='application/json'), 200
    except OperationFailure:
        return Response(json.dumps({
            "type": "success",
            "msg": "rolesInfo command failed. We assume that user doesn't have root privilege."
        }), mimetype='application/json'), 403


@app.route('/setup/verify/third_party_auth', methods=['POST'])
def setup_verify_tpauth():
    if request.values.get('UL_TP_REQUEST_FORMAT') is None or request.values.get('UL_TP_REQUEST_FORMAT') == '':
        data = {
            'username': '$username',
            'password': '$password'
        }
    else:
        data = json.loads(request.values.get('UL_TP_REQUEST_FORMAT'))

    try:
        res = requests.post(request.values.get('UL_TP_URL'), data=data)
        return Response(json.dumps({
            "type": "success",
            "msg": "Request has been successfully posted.",
            "res.text": res.text
        })), 200
    except:
        return Response(json.dumps({
            "type": "error",
            "msg": "Connection error. Host either unresolvable, or cannot be reach."
        })), 403

#
#
# @app.route('/test')
# def test():
#     alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
#     username = 'ul_user_' + ''.join(random.choice(alphabet) for i in range(5))
#     password = ''.join(random.choice(alphabet) for i in range(16))
#     client = mongo_client(
#         host='svc-nosql',
#         username='root',
#         password='root'
#     )
#     client.ul_login_db.command("createUser", username, pwd=password, roles=["readWrite"])
#     client.admin.command("createUser", username, pwd=password, roles=["readWrite"])
#     return Response('{"username":%s, "password":%s}' % (username, password), mimetype='application/json'), 200
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