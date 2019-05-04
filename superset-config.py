import os


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception.

    Args:
        var_name (str): the name of the environment variable to look up
        default (str): the default value if no env is found
    """
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        raise RuntimeError(
            'The environment variable {} was missing, abort...'
            .format(var_name)
        )


def get_secret(secret_name, default=None):
    """Get secrets mounted by kubernetes.

    Args:
        secret_name (str): the name of the secret, corresponds to the filename
        default (str): the default value if no secret is found
    """
    secret = None

    try:
        with open('/secrets/{0}'.format(secret_name), 'r') as secret_file:
            secret = secret_file.read().strip()
    except (IOError, FileNotFoundError):
        pass

    if secret is None:
        if default is None:
            raise RuntimeError(
                'Missing a required secret: {0}.'.format(secret_name)
            )
        secret = default

    return secret


# Postgres

POSTGRES_USER = get_secret('database/username')
POSTGRES_PASSWORD = get_secret('database/password')
POSTGRES_HOST = get_env_variable('DB_HOST')
POSTGRES_PORT = get_env_variable('DB_PORT', 5432)
POSTGRES_DB = get_env_variable('DB_NAME')

SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)


# Redis

REDIS_HOST = get_env_variable('REDIS_HOST')
REDIS_PORT = get_env_variable('REDIS_PORT', 6379)


# Celery

class CeleryConfig:
    BROKER_URL = 'redis://{0}:{1}/0'.format(REDIS_HOST, REDIS_PORT)
    CELERY_IMPORTS = ('superset.sql_lab',)
    CELERY_RESULT_BACKEND = 'redis://{0}:{1}/1'.format(REDIS_HOST, REDIS_PORT)
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig
