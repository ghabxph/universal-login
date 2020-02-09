from flask import request
from flask import Response
from jwcrypto import jwt
from jwcrypto import jwk
from lib.mongo import db
import bcrypt
import time
import json
import os


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
                # token.make_signed_token(os.environ.get('UL_KEY'))
                token.make_signed_token(jwk.JWK(**json.loads(os.environ.get('UL_KEY'))))
                return Response(json.dumps({"msg": "Login success.", "jws": token.serialize()}),
                                mimetype='application/json'), 200
        return Response(json.dumps({"msg": "Invalid username and/or password"}), mimetype='application/json'), 403
