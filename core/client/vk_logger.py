import logging.config


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
        logging.config.fileConfig('/home/bogdan/Projects/vkscraper/log_config')
        logging.getLogger("pika").setLevel(logging.WARNING)
        logging.getLogger("root").setLevel(logging.DEBUG)
        self.log = logging.getLogger('root')
