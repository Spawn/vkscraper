import os
import random
import time
import sys

from py_daemon.py_daemon import Daemon
from multiprocessing import Process
import test_conf


class Worker(Daemon):

    def check_kwargs(self, **kwargs):

        try:
            self.filename = kwargs['filename_for_output']
            self.path = kwargs['path']

            return True

        except KeyError as err:
            print 'Key %s was not found, check the test_conf.py' % err


class DoSomething(Worker):

    def __init__(self, pidfile, **kwargs):
        super(DoSomething, self).__init__(pidfile)

        if not self.check_kwargs(**kwargs):
            sys.exit(1)

    def run(self, **kwargs):
        writer = FileWriter(filename_for_output=self.filename, path=self.path)

        while True:
            writer.write_data('%s \n' % time.localtime())
            time.sleep(5)


class DoSomethingElse(Worker):

    def __init__(self, pidfile, **kwargs):
        super(DoSomethingElse, self).__init__(pidfile)

        if not self.check_kwargs(**kwargs):
            sys.exit(1)

    def run(self):
        writer = FileWriter(filename_for_output=self.filename, path=self.path)

        while True:
            writer.write_data(random.choice([i for i in xrange(101)]))
            time.sleep(5)


class FileWriter(object):

    def __init__(self, **kwargs):
        self.filename = kwargs['filename_for_output']
        self.path = kwargs['path']

    def write_data(self, data):

        try:
            with open(os.path.join(self.path, self.filename), 'a') as f:
                f.write(str(data))

        except IOError as err:
            print err


class Manager(object):

    def __init__(self, daemon=True):
        self.workers = test_conf.WORKERS
        if not self.workers:
            raise Exception('No one worker is specified, check the test_conf.py')
        self.daemon = daemon

    def _init_worker(self, worker_name):

        try:
            worker_config = self.workers[worker_name]
            worker_class = worker_config['class']

        except KeyError:
            print 'Invalid configs for %s' % worker_name
            return

        cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pids'))
        pidfile = os.path.join(cwd, worker_name)
        worker = worker_class(pidfile=pidfile, **worker_config)

        return worker

    def run_workers(self):
        processes = []

        for worker_name in self.workers:
            worker = self._init_worker(worker_name)

            process = Process(target=worker.start if self.daemon else worker.run)
            process.start()

        for process in processes:
            process.join()

if __name__ == '__main__':
    manage = Manager()
    manage.run_workers()
