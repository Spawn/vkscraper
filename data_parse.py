from pprint import pprint

from client import VKClient
from client import proxy_list
import gevent
from gevent import monkey


class VKData(object):
    def __init__(self):
        self.parameters = dict()
        self.client = None
        self.proxy_list = proxy_list

    def init_client_from_query(self):
        self.parameters = {
            'q': 'cat',
            'count': 40,
            'start_time': 1483056000,
            'end_time': 1484697600,
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def init_client_from_page(self):
        self.parameters = {
            'owner_id': 15723625,
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def init_client_update_posts(self):
        self.parameters = {
            'posts': '15723625_5801, 15723625_5800,15723625_5799,15723625_5798,15723625_5797,\
            15723625_5796,15723625_5795,15723625_5794,15723625_5793, 15723625_5792,15723625_5791,\
            15723625_5790,15723625_5789,15723625_5788,15723625_5787,15723625_5786,15723625_5784,\
            15723625_5783,15723625_5782,15723625_5779',
            'access_token': '',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def init_client_update_authors(self):
        self.parameters = {
            'user_ids': 'aqustics, katya_fofina',
            'fields': 'counters, photo_id',
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def from_query(self):
        self.init_client_from_query()
        data = self.client.newsfeed.search(**self.parameters)
        return data

    def from_page(self):
        self.init_client_from_page()
        data = self.client.wall.get(**self.parameters)
        return data

    def update_posts(self):
        jobs = []
        self.init_client_update_posts()
        posts = self.parameters['posts'].split(',')
        monkey.patch_all()
        for post in posts:
            self.parameters.update({'posts': post})
            jobs.append(gevent.spawn(self.client.wall.getById, **self.parameters))
            yield [res.get() for res in gevent.joinall(jobs)]

    def update_author(self):
        jobs = []
        self.init_client_update_authors()
        users = self.parameters['user_ids'].split(',')
        monkey.patch_all()
        for user in users:
            self.parameters.update({'user_ids': user})
            jobs.append(gevent.spawn(self.client.users.get, **self.parameters))
        # jobs = [gevent.spawn(self.client.users.get, self.parameters.update({'user_ids': user})) for user in users]
        yield [res.get() for res in gevent.joinall(jobs)]

a = VKData()
res = a.update_posts()
for item in res:
    pprint(item)
