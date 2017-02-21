import json

import gevent
import pika

from py_daemon.py_daemon import Daemon
from core.async_utils import AsyncRequests
from core.client import VKClient
from core.data_formatter import FormatAuthor, FormatPost
from proxies import DEFAULT_PROXY_LIST as default_proxy_list
from core.settings import RABBITMQ_CONF
from core.client.vk_logger import VKLogger


class SocialScraper(Daemon):
    pass


class VKScrapper(SocialScraper):
    """
    It allows to scrape data from VK
    """

    def __init__(self, pidfile=None, proxy_list=None):
        super(VKScrapper, self).__init__(pidfile)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_CONF['host'], port=RABBITMQ_CONF['port'], channel_max=20))
        self.proxy_list = proxy_list if proxy_list else default_proxy_list
        self.parameters = dict()
        self.client = None
        self.channel = None

    def _fetch_data(self, api_method, param_key):
        VKLogger.log.debug('BEGIN FETCHING DATA')
        async_requests = AsyncRequests(timeout=3)
        items = self.parameters[param_key].split(',')
        VKLogger.log.debug('ITEMS: %s' % items)

        for item in items:
            self.parameters.update({param_key: item})
            async_requests.add_job(gevent.spawn(api_method, **self.parameters))
        return async_requests.join_jobs()

    def _reformat_posts(self, posts):
        format_post = FormatPost()
        for post in posts:
            if len(post) != 0:
                yield format_post.as_dict(post)
            else:
                continue

    def _reformat_authors(self, posts):
        format_author = FormatAuthor()

        unique_authors = []
        for post in posts:
            if post and post.get('owner_id') not in unique_authors:
                unique_authors.append(str(post.get('owner_id')))

        authors = self.client.users.get(user_ids=','.join(unique_authors))
        for author in authors['items']:
            yield format_author.as_dict(author)

    def _get_authors_statistic(self, authors):
        statistic = FormatAuthor()
        for author in authors:
            yield statistic.as_dict(author['items'][0], statistic=True)

    def _get_posts_statistic(self, posts):
        statistic = FormatPost()
        for post in posts:
            if len(post['items']) != 0:
                yield statistic.get_post_statistics(post['items'][0])
            else:
                continue

    def init_scraper(self, scraper_name):
        """
        Initializes RabbitMQ channel and returns queue name.
        :param scraper_name:
        :return:
        """

        VKLogger.log.debug('START INIT')
        self.channel.exchange_declare(exchange=scraper_name,
                                      type='topic')

        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        VKLogger.log.debug(queue_name)
        self.channel.queue_bind(exchange=scraper_name,
                                queue=queue_name,
                                routing_key='#')
        return queue_name

    def process_data(self, parameters):
        """
        Must be implemented in each scraper for data processing.
        """
        raise NotImplementedError("Process data for this scraper not implemented.")

    def callback(self, ch, method, properties, body):
        """
        RabbitMQ callback. Initializes VKClient and call process data.
        """

        VKLogger.log.debug('CALLBACK BEGIN')
        self.parameters = json.loads(body)

        VKLogger.log.debug('PARAMETERS UNPACKED: %s' % self.parameters)

        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

        VKLogger.log.debug('CLIENT INITIALIZED: %s' % self.client)

        self.process_data(self.parameters)
        VKLogger.log.debug('CALLBACK END')

    def run(self, **kwargs):
        """
        Receives the scraper name and starts the listening rabbitmq queue.
        :param kwargs: Includes scraper name.
        """
        self.channel = self.connection.channel()
        queue_name = self.init_scraper(kwargs['scraper_name'])
        self.channel.basic_consume(self.callback,
                                   queue=queue_name,
                                   no_ack=True)

        VKLogger.log.debug('START LISTENING')
        self.channel.start_consuming()


class VKFromQuery(VKScrapper):

    def process_data(self, parameters):
        data = self.client.newsfeed.search(**self.parameters)

        formatted_posts = self._reformat_posts(data['items'])
        formatted_authors = self._reformat_authors(data['items'])

        for item in formatted_posts:
            with open(self.__class__.__name__, 'a') as f:
                f.write(str(item))

        for item in formatted_authors:
            with open(self.__class__.__name__, 'a') as f:
                f.write(str(item))

    def __str__(self):
        return self.__class__.__name__


class VKFromPage(VKScrapper):

    def process_data(self, parameters):
        data = self.client.wall.get(**self.parameters)

        formatted_posts = self._reformat_posts(data['items'])
        for item in formatted_posts:
            with open(self.__class__.__name__, 'a') as f:
                f.write(str(item))

    def __str__(self):
        return self.__class__.__name__


class VKUpdatePosts(VKScrapper):

    def process_data(self, parameters):
        data = self._fetch_data(param_key='posts', api_method=self.client.wall.getById)

        posts_statistic = self._get_posts_statistic(data)

        for item in posts_statistic:
            with open(self.__class__.__name__, 'a') as f:
                f.write(str(item))

    def __str__(self):
        return self.__class__.__name__


class VKUpdateAuthors(VKScrapper):

    def process_data(self, parameters):
        data = self._fetch_data(param_key='user_ids', api_method=self.client.users.get)

        author_statistic = self._get_authors_statistic(data)

        for item in author_statistic:
            with open(self.__class__.__name__, 'a') as f:
                f.write(str(item))

    def __str__(self):
        return self.__class__.__name__
