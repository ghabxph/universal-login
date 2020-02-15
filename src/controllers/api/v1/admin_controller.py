from flask import Response
from flask import request
from lib.util import random_str
from lib.util import config
from jwcrypto import jwt
from jwcrypto import jwk
import json
import bcrypt
import requests


class AdminController:

    @staticmethod
    def generate_new_token():
        """
        Generates admin token needed for other 'Universal Login' instance to authenticate themselves
        :return:
        """
        token = random_str(32)

        config('UL_ADMIN_PASSWORD', str(bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode()))

        return Response(json.dumps({
            "type": "success",
            "msg": "Token has been generated successfully. Please do not lose this token, as we only store the hash "
                   "in the server.",
            "token": token
        })), 200

    @staticmethod
    def manage_other_instance():
        """
        This server will try to login to other 'Universal Login' server and act as its manager.
        If failed, nothing will happen but it shall return an error message. If success, this server
        will change its state as a manager. This instance will now act as a manager for the target.
        :return:
        """

        # Gets manager token that is to be saved in the 'Client manager'
        res = requests.post('%s/api/v1/admin/login' % request.values.get('url'), data={
            "password": request.values.get('key')
        })

        if res.status_code != 200:
            return Response(json.dumps({
                "type": "error",
                "msg": "Login to other instance did not succeed."
            }), mimetype='application/json')

        # Locks /init route
        config('UL_LOCK_INIT', 'true')

        # Saves jws token returned by the server
        config('UL_INSTANCE_TOKEN', res.json().get('jws'))

        return Response(json.dumps({
            "type": "success",
            "msg": "Login to other instance succeeds. Please redirect to /manage",
            "redirect": res.json().get('redirect')
        }), mimetype='application/json'), 200

    @staticmethod
    def admin_login():
        """
        Checks if password submitted by client is correct. If it is, the server will return a
        signed JWT claim that proves the admin that it is an admin in this server.

        Login is only one time. Once someone claimed that they are the admin, this method shall
        be rendered useless.
        :return:
        """

        req_pass = request.values.get('password').encode('utf-8')
        adm_pass = config('UL_ADMIN_PASSWORD').encode('utf-8')

        admin_is_logged_in = config('UL_ADMIN_LOGGED_IN') is not None
        password_is_invalid = bcrypt.checkpw(req_pass, adm_pass) is False

        # Checks if someone already logged in to the server, or checks invalidity of password
        if admin_is_logged_in or password_is_invalid:
            return Response(json.dumps({
                "type": "error",
                "msg": "Request forbidden."
            }), mimetype='application/json'), 403

        # Locks the admin_login()
        config('UL_ADMIN_LOGGED_IN', 'true')

        # Generates JWK
        config('UL_ADMIN_KEY', jwk.JWK.generate(kty='oct', size=256).export())

        # Claim
        token = jwt.JWT(header={'alg': 'HS256'}, claims={'administrator': True})

        # Signs the JWT using the newly generated key
        token.make_signed_token(jwk.JWK(**json.loads(config('UL_ADMIN_KEY'))))

        # Returns successful response, and the jws token.
        return Response(json.dumps({
            "type": "success",
            "msg": "Login succeed.",
            "jws": token.serialize(),
            "redirect": "/manage"
        }), mimetype='application/json'), 200
