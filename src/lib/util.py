from flask import Response
import os
import random
import json


def essential_env_present():
    return config('UL_DB_HOST') is not None and \
            config('UL_DB_ROOT_USER') is not None and \
            config('UL_DB_ROOT_PASS') is not None and \
            config('UL_DB_NAME_PREFIX') is not None and \
            config('UL_TP_CHECK') is not None and \
            config('UL_TP_URL') is not None and \
            config('UL_TP_REQUEST_FORMAT') is not None


def random_str(n):
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for i in range(n))


def init_is_locked():
    return Response(json.dumps({
        "type": "error",
        "msg": "Unauthorized access."
    })), 403


def config(key, value=None):

    config_file = '/tmp/.config.json'

    # If .config.json does not exist, we'll create one.
    if os.path.exists(config_file) is False:
        f = open(config_file, 'w')
        f.write('{}')

        f.close()

    # Loads .config.json within it's current working directory
    with open(config_file, 'r+') as f_conf:

        # Loads the json to memory (as dictionary)
        j_conf = json.loads(f_conf.read())

    # Check if 'value' parameter is not set (one parameter call)
    if value is None:

        # Check if env[key] is not set
        if os.environ.get(key) is None and j_conf.get(key) is not None:

            # Sets the env[key] from the config (value can still be none)
            os.environ[key] = j_conf.get(key)

        # Returns env[key] (Value can still be none)
        return os.environ.get(key)

    # Otherwise, we assume at this point that we have 2 parameter (we'll set value to file and environment)
    j_conf[key] = os.environ[key] = value

    # Loads .config.json within it's current working directory
    with open(config_file, 'w') as f_conf:

        # Then updates the config.
        f_conf.write(json.dumps(j_conf))

    # Just echoes the given value
    return value
