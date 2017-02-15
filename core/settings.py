import os

LOG_CONFIG = '/code/log_config'
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))

RABBITMQ_CONF = {
    'host': 'rabbitmq',
    'port': 5672,
}

CONF = {
    'vk': {
        'modules': {
            'from.query': 'app.VKFromQuery',
            'from.page': 'app.VKFromPage',
            'update.authors': 'app.VKUpdateAuthors',
            'update.posts': 'app.VKUpdatePosts',
        }
    }
}
