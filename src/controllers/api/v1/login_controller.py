from lib.util import essential_env_present
from flask import request
from flask import Response
from flask import redirect
from jwcrypto import jwt
from jwcrypto import jwk
from lib.mongo import db
from lib.util import config
import bcrypt
import time
import json


class LoginController:

    @staticmethod
    def post():
        user = db()['users'].find_one({"username": request.values.get('username').lower()})

        if user is not None:
            valid_username = request.values.get('username').lower() == user['username'].lower()
            valid_password = bcrypt.hashpw(request.values.get('password').encode('utf-8'), user['password']) == user[
                'password']

            if valid_username and valid_password:
                token = jwt.JWT(header={'alg': 'HS256'}, claims={
                    'usr': user['username'],
                    'iat': int(time.time()),
                    'exp': int(time.time() + 900)
                })
                token.make_signed_token(jwk.JWK(**json.loads(config('UL_KEY'))))
                return Response(json.dumps({
                    "type": "success",
                    "msg": "Login success.",
                    "jws": token.serialize()
                }), mimetype='application/json'), 200
        return Response(json.dumps({"msg": "Invalid username and/or password"}), mimetype='application/json'), 403

    @staticmethod
    def render_login():
        # Check all essential environment variable
        if not essential_env_present():
            # Redirects to setup page
            return redirect('/')

        with open('/html/login.html', 'r') as html:
            return html.read()
