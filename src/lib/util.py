from pymongo import MongoClient as db_client
import os


def essential_env_present():
    return os.environ.get('UL_DB_HOST') is not None and \
            os.environ.get('UL_DB_USER') is not None and \
            os.environ.get('UL_DB_PASS') is not None and \
            os.environ.get('UL_DB_NAME') is not None and \
            os.environ.get('UL_TP_CHECK') is not None and \
            os.environ.get('UL_TP_URL') is not None and \
            os.environ.get('UL_TP_METHOD') is not None and \
            os.environ.get('UL_TP_USER_FIELD') is not None and \
            os.environ.get('UL_TP_PASS_FIELD') is not None and \
            os.environ.get('UL_TP_OTHER_FIELDS') is not None


def set_essential_env(essential_env):
    for key in essential_env:
        if essential_env[key] is None:
            os.environ[key] = ''
        else:
            os.environ[key] = essential_env[key]


def validate_submitted_env(essential_env):
    client = db_client('mongodb://%s:%s@%s' % (
        essential_env['UL_DB_HOST'],
        essential_env['UL_DB_USER'],
        essential_env['UL_DB_PASS']
    ))
    return {
        'client': client.server_info(),
        'valid': False
    }
