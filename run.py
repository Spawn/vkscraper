import os
import argparse
import signal
import time
import settings
import logging

from multiprocessing import Process

from core.client.exceptions import InitializeException


class Manager(object):
    """
    It allows to start parsers which are specified in the setting.py
    """

    def __init__(self, arguments=None, daemon=True):
        self.arguments = arguments
        self.workers = settings.CONF
        self.daemon = daemon
        self.cwd = os.path.abspath(os.path.dirname(__file__))
        self.pids_dir = os.path.join(self.cwd, 'pids')
        self.modules = []
        self.scrapers = []
        self.action = getattr(arguments, 'action')
        self.api_methods = getattr(arguments, 'api_methods')

        if self.api_methods == '*:*':
            for scraper in settings.CONF:
                self.scrapers.append(scraper)
                for module_name in settings.CONF[scraper]['modules'].keys():
                    self.modules.append(module_name)
        else:
            self.modules = self.api_methods.split(':')
            self.scrapers.append(self.modules.pop(0))

        if not self.modules or not self.modules[0]:
            logging.fatal('No one correct module is specified, check the settings.py')
            raise InitializeException('No one correct module is specified, check the settings.py')

        logging.debug('Modules %s has been initialized' % self.modules)
        logging.info('Manager initialized')

    def _init_worker(self, module_name, scraper_name):
        """
        Receives the module and scraper names through that gets the workers classes from settings.py
        Returns initialized worker instance
        :param module_name:
        :param scraper_name:
        :return: instance
        """

        pidfile = os.path.join(self.pids_dir, module_name)
        try:
            instance = settings.CONF[scraper_name]['modules'][module_name](pidfile=pidfile)
        except KeyError as err:
            logging.warning('The not correct scraper or module are selected: %s' % err)
            return

        return instance

    def start_worker(self, scraper_name):
        """
        Receives the name of scraper.
        Initializes the workers in the loop and runs them in separate processes.
        :param scraper_name:
        :return: None
        """

        processes = []

        for module in self.modules:
            worker = self._init_worker(module, scraper_name)

            if not worker:
                continue

            process = Process(target=worker.start if self.daemon else worker.run)
            process.start()
            processes.append(process)

            logging.debug('Worker %s have been running' % worker)

        for process in processes:
            process.join()

    def run_scrapers(self):
        """
        Runs the workers of the each scraper.
        """
        for scraper in self.scrapers:
            self.start_worker(scraper)

    def restart_workers(self):
        pass

    def stop_workers(self):
        for method in self.api_methods:

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
            logging.info('Workers started')
            self.run_scrapers()
        elif self.action == 'restart':
            logging.info('Workers restarted')
            self.restart_workers()
        elif self.action == 'stop':
            logging.info('Workers stopped')
            self.stop_workers()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Pacing data from VK')
    parser.add_argument('--action', help='For workers manage. Allows start|restart|stop')
    parser.add_argument('--api_methods', help='Required the scraper name and it method(s). '
                                              'Example: vk:from.query:from.page. '
                                              'Command *:* runs all scrapers and workers.')
    parser.add_argument('--daemon', default=True, help='Flag to running workers as daemons. '
                                                     'Default: True', )
    args = parser.parse_args()
    logging.basicConfig(format=u'[%(asctime)s] %(levelname)-4s %(filename)s'
                               u' [LINE:%(lineno)d] %(funcName)s # %(message)s',
                        level=logging.DEBUG)
    runner = Manager(args, daemon=args.daemon)
    runner.execute()
