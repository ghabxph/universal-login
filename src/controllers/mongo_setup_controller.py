from flask import request
from flask import redirect
from flask import Response
from lib.util import essential_env_present
from lib.util import random_str
from pymongo import MongoClient as mongo_client
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure
from jwcrypto import jwk
import os
import bcrypt
import json
import requests


class MongoSetupController:

    @staticmethod
    def get():
        with open('/html/setup.html', 'r') as html_file:
            # index.html file
            html = html_file.read()

            # Check all essential environment variable
            if essential_env_present():
                # Perform URL redirection (to /login)
                return redirect('/login')

            # Perform re-setup.
            return Response(html), 200

    @staticmethod
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
        client[os.environ.get('UL_DB_NAME')].users.insert_one(
            {"username": "admin", "password": bcrypt.hashpw(b'admin', bcrypt.gensalt())})

        # Assign a random username and password for universal login user account
        os.environ['UL_DB_USER'] = 'ul_user_' + random_str(5)
        os.environ['UL_DB_PASS'] = random_str(16)

        # Creates a user dedicated for universal login only
        client[os.environ.get('UL_DB_NAME')].command("createUser", os.environ.get('UL_DB_USER'),
                                                     pwd=os.environ.get('UL_DB_PASS'), roles=["readWrite"])

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

    @staticmethod
    def setup_verify_mongodb():
        client = mongo_client(host=request.values.get('UL_DB_HOST'), serverSelectionTimeoutMS=5000)
        try:
            return Response(json.dumps({
                "type": "success",
                "msg": "Connection to mongodb host is successful.",
                "server_info": client.server_info()
            }, indent=4), mimetype='application/json'), 200
        except ServerSelectionTimeoutError:
            return Response(
                '{"type":"error", "msg":"Unable to connect to mongodb host. Are you sure that the hostname is reachable?"}',
                mimetype='application/json'), 403

    @staticmethod
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

    @staticmethod
    def setup_verify_mongodbadminpower():
        client = mongo_client(
            host='svc-nosql',
            serverSelectionTimeoutMS=500
        )
        try:
            client.admin.authenticate(name=request.values.get('UL_DB_ROOT_USER'),
                                      password=request.values.get('UL_DB_ROOT_PASS'))
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

    @staticmethod
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
            })),

    @staticmethod
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