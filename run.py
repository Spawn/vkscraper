import os
import argparse
from multiprocessing import Process
from sys import argv

import settings


class MultiRunner(object):

    def initial(self, arguments=None, as_daemon=True):
        cwd = os.path.abspath(os.path.dirname(__file__))
        if arguments:
            action = getattr(arguments, 'action')
            methods = getattr(arguments, 'methods')
            methods = methods.split(':')
            scrapper = methods.pop(0)
        else:
            arguments = argv
            action = arguments[1]
            methods = arguments[2]
            methods = methods.split(':')
            scrapper = methods.pop(0)
        for method in methods:
            if action == 'start' and not as_daemon:
                instance = settings.CONF[scrapper]['modules'][method]()
                instance.run()
            else:
                pidfile = os.path.join(cwd, method)
                instance = settings.CONF[scrapper]['modules'][method](pidfile=pidfile)
                process = Process(target=getattr(instance, action))
                process.start()
                process.join()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Pacing data from VK')
    parser.add_argument('action')
    parser.add_argument('methods')
    args = parser.parse_args()
    runner = MultiRunner()
    runner.initial(args)
