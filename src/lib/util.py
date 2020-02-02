import os


def essential_env_present():
    return os.environ.get('UL_DB_HOST') is not None and \
            os.environ.get('UL_DB_ROOT_USER') is not None and \
            os.environ.get('UL_DB_ROOT_PASS') is not None and \
            os.environ.get('UL_DB_NAME_PREFIX') is not None and \
            os.environ.get('UL_TP_CHECK') is not None and \
            os.environ.get('UL_TP_URL') is not None and \
            os.environ.get('UL_TP_REQUEST_FORMAT') is not None


def set_essential_env(essential_env):
    for key in essential_env:
        if essential_env[key] is None:
            os.environ[key] = ''
        else:
            os.environ[key] = essential_env[key]
