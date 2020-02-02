import os


def essential_env_present():
    return os.environ.get('UL_DB_HOST') is not None and \
            os.environ.get('UL_DB_ROOT_USER') is not None and \
            os.environ.get('UL_DB_ROOT_PASS') is not None and \
            os.environ.get('UL_DB_NAME_PREFIX') is not None and \
            os.environ.get('UL_TP_CHECK') is not None and \
            os.environ.get('UL_TP_URL') is not None and \
            os.environ.get('UL_TP_REQUEST_FORMAT') is not None
