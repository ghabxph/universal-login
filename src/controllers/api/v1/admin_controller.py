from flask import Response
from lib.util import random_str
import os
import json
import bcrypt


class AdminController:

    @staticmethod
    def generate_new_token():
        """

        :return:
        """
        token = random_str(32)

        os.environ['ADMIN_TOKEN'] = str(bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode())

        return Response(json.dumps({
            "type": "success",
            "msg": "Token has been generated successfully. Please do not lose this token, as we only store the hash "
                   "in the server.",
            "token": token
        })), 200
