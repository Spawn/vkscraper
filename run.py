import os
import argparse
from multiprocessing import Process
from sys import argv

import signal

import time

import settings


class Manager(object):

    def __init__(self, arguments=None, daemon=True):
        self.args = args
        self.workers = settings.CONF
        self.daemon = daemon
        self.cwd = os.path.abspath(os.path.dirname(__file__))
        self.pids_dir = os.path.join(self.cwd, 'pids')

        if not self.workers:
            raise Exception('No one worker is specified, check the settings.py')

        elif arguments:
            self.action = getattr(arguments, 'action')
            self.methods = getattr(arguments, 'methods')
            self.methods = self.methods.split(':')
            self.scrapper = self.methods.pop(0)
        else:
            arguments = argv
            self.action = arguments[1]
            self.methods = arguments[2]
            self.methods = self.methods.split(':')
            self.scrapper = self.methods.pop(0)

    def _init_worker(self, method):
        pidfile = os.path.join(self.pids_dir, method)
        if self.methods == '*':
            pass
        try:
            instance = settings.CONF[self.scrapper]['modules'][method](pidfile=pidfile)
        except KeyError as err:
            print 'The not correct instance or method are selected: %s' % err
            return

        return instance

    def start_workers(self):
        processes = []

        for method in self.methods:
            worker = self._init_worker(method)

            if not worker:
                continue

            process = Process(target=worker.start if self.daemon else worker.run)
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    def restart_workers(self):
        pass

    def stop_workers(self):
        for method in self.methods:

            with open(os.path.join(self.pids_dir, method), 'r') as f:
                pid = int(f.read().strip())
                i = 0

                while True:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
                    i += 1

                    if i == 10:
                        os.kill(pid, signal.SIGHUP)

    def execute(self):
        if self.action == 'start':
            self.start_workers()
        elif self.action == 'restart':
            self.restart_workers()
        elif self.action == 'stop':
            self.stop_workers()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Pacing data from VK')
    parser.add_argument('action')
    parser.add_argument('methods')
    args = parser.parse_args()
    runner = Manager(args)
    runner.execute()
