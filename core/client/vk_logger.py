import logging.config
import os
from core.settings import LOG_CONFIG, LOG_DIR


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class VKLogger(object):
    def __init__(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        logging.config.fileConfig(LOG_CONFIG)
        logging.getLogger("pika").setLevel(logging.WARNING)
        logging.getLogger("root").setLevel(logging.DEBUG)
        self.log = logging.getLogger('root')
