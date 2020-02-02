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


# @status: Done, not yet tested
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


# @status: Under development
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
