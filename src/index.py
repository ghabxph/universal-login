from flask import Flask
from flask import jsonify
from jwcrypto import jwt, jwk, jws
from controllers.api.v1.login_controller import LoginController
from controllers.assets_controller import AssetsController
from controllers.init_controller import InitController
from controllers.mongo_setup_controller import MongoSetupController
from controllers.api.v1.admin.token_controller import TokenController as admin_token
import json

# Essential Instances
app = Flask(__name__)


@app.route('/test')
def test():
    key = jwk.JWK.generate(kty='EC', crv='P-256')
    return jsonify({
        'with_private': json.loads(key.export()),
        'without_private': json.loads(key.export(private_key=False))
    })


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
    return MongoSetupController.setup_verify_mongodb()


@app.route('/setup/get_environment', methods=['GET'])
def setup_get_environment():
    return MongoSetupController.setup_get_environment()


@app.route('/login', methods=['GET'])
def render_login():
    return LoginController.render_login()


@app.route('/init', methods=['GET'])
def init():
    return InitController().index()


# All api/v1 routes


@app.route('/api/v1/login', methods=['POST'])
def login():
    return LoginController.post()

@app.route('/api/v1/admin/token', methods=['POST'])
def generate_new_token():
    return admin_token.generate_new_token()

# -----------------------------------------

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