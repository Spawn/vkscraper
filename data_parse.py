from pprint import pprint

from client import VKClient
from client import proxy_list as default_proxy_list
import gevent
from gevent import monkey
monkey.patch_all()


class AsyncRequests(object):

    def __init__(self, timeout):
        self.jobs_pull = []
        self.timeout = timeout

    def add_job(self, job):
        self.jobs_pull.append(job)

    def join_jobs(self):
        timeout = len(self.jobs_pull) * self.timeout
        for result in gevent.joinall(self.jobs_pull, timeout=timeout):
            yield result.get()


class VKData(object):
    def __init__(self, proxy_list=None):
        self.proxy_list = proxy_list if proxy_list else default_proxy_list
        self.parameters = dict()
        self.client = None

    def _fetch_data(self, method, param_key):
        async_requests = AsyncRequests(timeout=3)
        items = self.parameters[param_key].split(',')
        for item in items:
            self.parameters.update({param_key: item})
            async_requests.add_job(gevent.spawn(method, **self.parameters))
        return async_requests.join_jobs()

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
            15723625_5783,15723625_5782,43291122_33348,15723625_5806',
            'access_token': '',
            'extended': '1',
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
        self.init_client_update_posts()
        return self._fetch_data(param_key='posts', method=self.client.wall.getById)

    def update_author(self):
        self.init_client_update_authors()
        return self._fetch_data(param_key='user_ids', method=self.client.users.get)


class DataFormatting(object):

    def __init__(self, data_list):
        self.data_list = data_list
        self.output_post = {}

    def _get_post_type(self, item):

        ATTACHMENT_TYPES = {
            'photo': 1,
            'video': 2,
            'link': 3,
        }

        if 'attachments' in item:
            attachment_type = item['attachments'][0]['type']
            for attachment in item['attachments']:
                if attachment_type != attachment['type']:
                    return 4
                return ATTACHMENT_TYPES[attachment_type]

        elif 'text' in item:
            return 0

        return 'no data'

    def _get_post_from_list(self):
        for post in self.data_list:
            yield post

    def _get_original_post(self, post):
        original_post = post['items']['copy_history']
        return original_post

    def _get_thumbnail(self, content):
        max_size = 0
        url = ''
        for key, value in content.items():
            if key.startswith('photo_'):
                size = key.split('_')[1]
                if size > max_size:
                    max_size = size
                    url = value
        return url

    def _get_attachments(self, item):
        for attachment in item['attachments']:
            attachment_type = attachment['type']
            attachment_content = attachment[attachment_type]
            url = 'https://vk.com/' + attachment_type + attachment_content['id'] + '_' + attachment_content['owner_id']
            self.output_post[attachment_type].append({'url': url,
                                                      'thumbnail': self._get_thumbnail(attachment_content)})

    def forming_post_dict(self):
        posts = self.data_list

        for post in posts:
            item = post['items'][0]
            self._get_post_type(item)

            if 'copy_history' in item:
                self.output_post['original_post'] = self._get_original_post(post)  # todo formatting origin post under basic

            self.output_post['post_type'] = self._get_post_type(item)
            self.output_post['vk_ids'] = {'post_id': item['id'],
                                          'author_id': item['owner_id']}

            if self.output_post['post_type'] != 0 and self.output_post['post_type'] != 'no data':
                self._get_attachments(item)



    def forming_unique_authors(self):
        pass

a = VKData()
res = a.update_posts()

# data_formatting = DataFormatting(res)
# data_formatting.forming_post_dict()

for item in res:
    pprint(item)
