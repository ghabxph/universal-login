from flask import Flask
from flask import Response
from flask import request
from flask import redirect
from flask import jsonify
from lib.util import essential_env_present
from lib.util import random_str
from pymongo import MongoClient as mongo_client
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure
from requests.exceptions import ConnectionError
from jwcrypto import jwt, jwk, jws
from lib.mongo import db
from controllers.init_controller import InitController
import os
import json
import random
import requests
import bcrypt
import time
import sys

# Essential Instances
app = Flask(__name__)


@app.route('/test')
def test():
    key = jwk.JWK.generate(kty='EC', crv='P-256')
    return jsonify({
        'with_private': json.loads(key.export()),
        'without_private': json.loads(key.export(private_key=False))
    })


@app.route('/api/v1/login', methods=['POST'])
def login():
    user = db()['users'].find_one({"username": request.values.get('username').lower()})

    if user is not None:
        valid_username = request.values.get('username').lower() == user['username'].lower()
        valid_password = bcrypt.hashpw(request.values.get('password').encode('utf-8'), user['password']) == user['password']

        if valid_username and valid_password:

            token = jwt.JWT(header={'alg': 'HS256'}, claims={
                'usr': user['username'],
                'iat': int(time.time()),
                'exp': int(time.time() + 900)
            })
            # token.make_signed_token(os.environ.get('UL_KEY'))
            token.make_signed_token(jwk.JWK(**json.loads(os.environ.get('UL_KEY'))))
            return Response(json.dumps({"msg": "Login success.", "jws": token.serialize()}), mimetype='application/json'), 200
    return Response(json.dumps({"msg": "Invalid username and/or password"}), mimetype='application/json'), 403


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

        # Redirects to /login page
        return redirect('/login')

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

    # Create a client instance (mongodb)
    client = mongo_client(
        host=os.environ.get('UL_DB_HOST'),
        username=os.environ.get('UL_DB_ROOT_USER'),
        password=os.environ.get('UL_DB_ROOT_PASS')
    )

    # Assigns database name from prefix
    os.environ['UL_DB_NAME'] = os.environ.get('UL_DB_NAME_PREFIX') + 'ul_db'

    # Creates an initial user: admin:admin
    # Note that this will have issue if we have third party authentication server.
    # I will make a separate setup for this, but for now, the implementation would be
    # just this simple. I will not handle third party auth for now...
    client[os.environ.get('UL_DB_NAME')].users.insert_one({"username": "admin", "password": bcrypt.hashpw(b'admin', bcrypt.gensalt())})

    # Assign a random username and password for universal login user account
    os.environ['UL_DB_USER'] = 'ul_user_' + random_str(5)
    os.environ['UL_DB_PASS'] = random_str(16)

    # Creates a user dedicated for universal login only
    client[os.environ.get('UL_DB_NAME')].command("createUser", os.environ.get('UL_DB_USER'), pwd=os.environ.get('UL_DB_PASS'), roles=["readWrite"])

    # Generate a symmetric key
    # Note: I wish to use asymmetric key, but I have issues with EC or RSA.
    # Errors: TypeError: object of type '_RSAPrivateKey' has no len() or
    #         TypeError: object of type '_EllipticCurvePrivateKey' has no len()
    os.environ['UL_KEY'] = jwk.JWK.generate(kty='oct', size=256).export()

    # Set environment from submitted form
    with open('/html/setup-done.html', 'r') as html_file:

        # index.html file
        html = html_file.read()

        # Check all essential environment variable
        if essential_env_present():
            # Perform re-setup.
            return Response(html), 200

        # Perform URL redirection
        return redirect('/')


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


@app.route('/setup/get_environment', methods=['GET'])
def setup_get_environment():

    if os.environ.get('UL_ENV_SHOWN') == 'true':
        return Response(json.dumps({
            "type": "error",
            "msg": "You are not authorized to view this page."
        }), mimetype='application/json'), 403

    # Mark UL_ENV_SHOWN so that server won't be allowed to show the info again.
    os.environ['UL_ENV_SHOWN'] = 'true'

    return Response(json.dumps({
        "type": "success",
        "msg": "Environment variable retrieval succeed. Please look at env variable.",
        "env": {
            "UL_KEY": os.environ.get('UL_KEY'),
            "UL_DB_HOST": os.environ.get('UL_DB_HOST'),
            "UL_DB_ROOT_USER": os.environ.get('UL_DB_ROOT_USER'),
            "UL_DB_ROOT_PASS": os.environ.get('UL_DB_ROOT_PASS'),
            "UL_DB_NAME_PREFIX": os.environ.get('UL_DB_NAME_PREFIX'),
            "UL_DB_USER": os.environ.get('UL_DB_USER'),
            "UL_DB_PASS": os.environ.get('UL_DB_PASS'),
            "UL_DB_NAME": os.environ.get('UL_DB_NAME'),
            "UL_TP_CHECK": os.environ.get('UL_TP_CHECK'),
            "UL_TP_URL": os.environ.get('UL_TP_URL'),
            "UL_TP_REQUEST_FORMAT": os.environ.get('UL_TP_REQUEST_FORMAT')
        }
    }), mimetype='application/json'), 200


@app.route('/login', methods=['GET'])
def render_login():

    # Check all essential environment variable
    if not essential_env_present():

        # Redirects to setup page
        return redirect('/')

    with open('/html/login.html', 'r') as html:
        return html.read()


@app.route('/init', methods=['GET'])
def init():
    return InitController().index()
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