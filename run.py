import os
import argparse
import signal
import time

import sys

import settings

from multiprocessing import Process
from core.client.exceptions import InitializeException
from core.client.vk_logger import VKLogger


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

        if not os.path.exists(self.pids_dir):
            os.makedirs(self.pids_dir)

        if self.api_methods == '*:*':
            for scraper in settings.CONF:
                self.scrapers.append(scraper)
                for module_name in settings.CONF[scraper]['modules'].keys():
                    self.modules.append(module_name)
        else:
            self.modules = self.api_methods.split(':')
            self.scrapers.append(self.modules.pop(0))

        if not self.modules or not self.modules[0]:
            VKLogger.log.fatal('No one correct module is specified, check the settings.py')
            raise InitializeException('No one correct module is specified, check the settings.py')

        VKLogger.log.debug('Modules %s has been initialized' % self.modules)
        VKLogger.log.info('Manager initialized')

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
            VKLogger.log.warning('The not correct scraper or module are selected: %s' % err)
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

            process = Process(target=worker.start if self.daemon else worker.run, kwargs={'scraper_name': module})
            process.start()
            processes.append(process)

            VKLogger.log.debug('Worker %s have been running' % worker)

        for process in processes:
            process.join()

    def run_scrapers(self):
        """
        Runs the workers of the each scraper.
        """

        for scraper in self.scrapers:
            self.start_worker(scraper)

    def stop_scrapers(self):
        """
        Stops workers of the each scraper via pidfile
        """

        def stop_worker(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())

                    i = 0
                    try:
                        while True:
                            os.kill(pid, signal.SIGTERM)
                            time.sleep(0.1)
                            i += 1

                            if i == 10:
                                os.kill(pid, signal.SIGHUP)
                    except OSError:
                        VKLogger.log.info('Worker with pid %s stopped' % pid)
                        os.remove(pid_file)
            except ValueError:
                print 'Invalid pidfile'

        if self.api_methods == '*:*':
            for filename in os.listdir(self.pids_dir):
                stop_worker('{}/{}'.format(self.pids_dir, filename))
        else:
            for method in self.api_methods.split(':')[1:]:
                try:
                    stop_worker(os.path.join(self.pids_dir, method))
                except IOError:
                    VKLogger.log.warning('Pidfile for worker %s does not exist' % method)

    def execute(self):

        if self.action == 'start':
            self.run_scrapers()
            VKLogger.log.info('Workers started')
        elif self.action == 'restart':
            self.stop_scrapers()
            self.run_scrapers()
            VKLogger.log.info('Workers restarted')
        elif self.action == 'stop':
            self.stop_scrapers()
            VKLogger.log.info('Workers stopped')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Pacing data from VK')
    parser.add_argument('action', help='For workers manage. Allows start|restart|stop')
    parser.add_argument('api_methods', help='Required the scraper name and it method(s). '
                                            'Example: vk:from.query:from.page. '
                                            'Command *:* selects all scrapers and workers.')
    parser.add_argument('--daemon', default=True, help='Flag to running workers as daemons. '
                                                       'Default: True', )
    args = parser.parse_args()
    if args.daemon == 'True':
        args.daemon = True
    elif args.daemon == 'False':
        args.daemon = False
    else:
        print 'Use --daemon True or --daemon False'
        sys.exit(1)
    runner = Manager(args, daemon=args.daemon)
    runner.execute()
