from pprint import pprint
import time

from datetime import datetime

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
            15723625_5783,15723625_5782,43291122_33348,15723625_5806,15723625_5808,15723625_5809',
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

    def _get_post_type(self, item):

        ATTACHMENT_TYPES = {
            'photo': 1,
            'video': 2,
            'link': 3,
        }

        if 'attachments' in item:
            [item['attachments'].pop(x) for x in xrange(len(item['attachments']) - 1, -1, -1) if
             'audio' in item['attachments'][x]]
            attachment_type = item['attachments'][0]['type']
            for attachment in item['attachments']:
                if attachment_type != attachment['type']:
                    return 4
                return ATTACHMENT_TYPES[attachment_type]

        elif item.get('text'):
            return 0

        return 'no data'

    def _get_original_post(self, post):
        original_post = post['items'][0]['copy_history']
        return original_post

    def _get_thumbnail(self, content):
        max_size = 0
        url = ''
        for key, value in content.items():
            if key.startswith('photo_'):
                size = int(key.split('_')[1])
                if size > max_size:
                    max_size = size
                    url = value
        return url

    def _get_attachments(self, item):
        attachments = {}

        for attachment in item['attachments']:
            attachment_type = attachment['type']
            attachment_content = attachment[attachment_type]
            if attachment_type == 'link':
                url = attachment_content.get('url')
            else:
                url = 'https://vk.com/' + attachment_type + \
                      str(attachment_content['owner_id']) + \
                      '_' + str(attachment_content['id'])

            if attachment_type not in attachments:
                attachments[attachment_type] = list()
            attachments[attachment_type].append({'url': url,
                                                 'thumbnail': self._get_thumbnail(attachment_content)})
        return attachments

    def _get_vk_ids(self, item):
        post_id = item.get('id')
        owner_id = item.get('owner_id')
        return {'post_id': post_id, 'author_id': owner_id}

    def _get_post_url(self, item):
        owner_id = str(item.get('owner_id'))
        post_id = str(item.get('id'))
        return 'https://vk.com/wall' + owner_id + '_' + post_id

    def _get_publish_date(self, item):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(item.get('date')))

    def _get_content(self, item):
        return item.get('text')

    def _get_statistics(self, item):
        likes = item.get('likes')
        comments = item.get('comments')
        shares = item.get('reposts')
        last_updated = datetime.now()
        if not likes or not comments or not shares:
            return 'Empty'
        else:
            return {'likes': likes['count'],
                    'comments': comments['count'],
                    'shares': shares['count'],
                    'last_updated': last_updated}

    def forming_post_dict(self, posts):
        formatted_post = {}

        for post in posts:
            if 'items' in post:
                if len(post['items']) != 0:
                    item = post['items'][0]
                else:
                    continue
            else:
                item = post

            if 'copy_history' in item:
                original_post = self._get_original_post(post)
                formatted_post['original_post'] = list(self.forming_post_dict(original_post))[0]

            formatted_post['url'] = self._get_post_url(item)
            formatted_post['published_at'] = self._get_publish_date(item)
            formatted_post['post_type'] = self._get_post_type(item)
            formatted_post['vk_ids'] = self._get_vk_ids(item)
            formatted_post['content'] = self._get_content(item)
            formatted_post['statistic'] = self._get_statistics(item)

            if formatted_post['post_type'] != 0 and formatted_post['post_type'] != 'no data':
                formatted_post.update(self._get_attachments(item))
            yield formatted_post

    def forming_unique_authors(self, posts):
        unique_authors = []
        for post in posts:
            item = post.get('items')
            if item and item[0].get('owner_id') not in unique_authors:
                unique_authors.append(item[0].get('owner_id'))
        return unique_authors

a = VKData()
res = a.update_posts()
result = list(res)  # res - generator
data_formatting = DataFormatting()
posts = data_formatting.forming_post_dict(result)

pprint(list(posts))
authors = data_formatting.forming_unique_authors(result)
pprint(authors)
