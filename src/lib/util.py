import os


def check_essential_env():
    return os.environ.get('UL_DB_HOST') is not None or \
            os.environ.get('UL_DB_USER') is not None or \
            os.environ.get('UL_DB_PASS') is not None or \
            os.environ.get('UL_DB_NAME') is not None or \
            os.environ.get('UL_TP_CHECK') is not None or \
            os.environ.get('UL_TP_URL') is not None or \
            os.environ.get('UL_TP_METHOD') is not None or \
            os.environ.get('UL_TP_USER_FIELD') is not None or \
            os.environ.get('UL_TP_PASS_FIELD') is not None or \
            os.environ.get('UL_TP_OTHER_FIELDS') is not None
