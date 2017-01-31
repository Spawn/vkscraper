import types
import argparse
from pprint import pprint
from multiprocessing import Pool
from app import VKData


def to_list_cb(instance, method):
    def cb():
        data_list = []
        for item in getattr(instance, method)():
            data_list.append(list(item) if isinstance(item, types.GeneratorType) else item)
        return data_list
    return cb()


class MultiRunner(object):

    ALLOWED_METHODS = [
        'from_query',
        'from_page',
        'update_posts',
        'update_authors',
    ]

    def __init__(self, **kwargs):
        ACTIONS = {
            'start': self.start,
            'stop': self.stop,
            'restart': self.restart
        }

        self.methods = kwargs['methods']
        try:
            ACTIONS[kwargs['action']]()
        except KeyError as err:
            print 'This action is not allowed: {}'.format(err)

    def start(self):
        instance = VKData()
        if self.methods == '*:*':
            list_methods = self.ALLOWED_METHODS
        else:
            self.methods = self.methods.replace('.', '_')
            list_methods = self.methods.split(':')[1:]
        pool = Pool(processes=len(list_methods))
        for process in list_methods:
            pprint(pool.apply_async(to_list_cb, args=(instance, process)).get())

        pool.close()
        pool.join()

    def stop(self):
        pass

    def restart(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pacing data from VK')
    parser.add_argument('action')
    parser.add_argument('methods')
    args = parser.parse_args()
    runner = MultiRunner(action=args.action, methods=args.methods)
