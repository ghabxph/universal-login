from flask import Flask
from flask import Response
from flask import request
from flask import redirect
from flask import jsonify
from lib.util import essential_env_present
from jwcrypto import jwt, jwk, jws
from controllers.api.v1.login_controller import LoginController
from controllers.assets_controller import AssetsController
from controllers.init_controller import InitController
from controllers.mongo_setup_controller import MongoSetupController
import os
import json
import requests

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
    return LoginController.post()


@app.route('/assets')
def assets():
    return AssetsController.get()


@app.route('/', methods=['GET'])
def setup():
    return MongoSetupController.get()


# @status: Under development
@app.route('/', methods=['POST'])
def set_environment():
    return MongoSetupController.set_environment()


@app.route('/setup/verify/mongodb', methods=['POST'])
def setup_verify_mongodb():
    return MongoSetupController.setup_verify_mongodb()


@app.route('/setup/verify/mongodb_admin_user', methods=['POST'])
def setup_verify_mongodbadminuser():
    return MongoSetupController.setup_verify_mongodbadminuser()


@app.route('/setup/verify/mongodb_admin_power', methods=['POST'])
def setup_verify_mongodbadminpower():
    return MongoSetupController.setup_verify_mongodbadminpower()


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