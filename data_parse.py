from client import VKClient
from client import proxy_list


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
            'access_token': '434c78c2a0357b058d84e1390dbf32d59e0b2adc7ec8efd3ee0a8d400b309271858c28c4184746fbc83c6',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def init_client_from_page(self):
        self.parameters = {
            'owner_id': 15723625,
            'access_token': '434c78c2a0357b058d84e1390dbf32d59e0b2adc7ec8efd3ee0a8d400b309271858c28c4184746fbc83c6',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def init_client_update_posts(self):
        self.parameters = {
            'posts': '15723625_5801, 15723625_5800,15723625_5799,15723625_5798,15723625_5797,\
            15723625_5796,15723625_5795,15723625_5794,15723625_5793, 15723625_5792,15723625_5791,\
            15723625_5790,15723625_5789,15723625_5788,15723625_5787,15723625_5786,15723625_5784,\
            15723625_5783,15723625_5782,15723625_5779',
            'access_token': '434c78c2a0357b058d84e1390dbf32d59e0b2adc7ec8efd3ee0a8d400b309271858c28c4184746fbc83c6',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def init_client_update_authors(self):
        self.parameters = {
            'user_ids': 'aqustics',
            'fields': 'counters, photo_id',
            'access_token': '434c78c2a0357b058d84e1390dbf32d59e0b2adc7ec8efd3ee0a8d400b309271858c28c4184746fbc83c6',
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
        self.init_client_update_posts()
        data = self.client.wall.getById(**self.parameters)
        return data

    def update_author(self):
        self.init_client_update_authors()
        data = self.client.users.get(**self.parameters)
        return data

a = VKData()
data = a.update_author()
for item in data['items']:
    print item
