import hashlib
from datetime import datetime
from pprint import pprint
from uuid import UUID

import gevent
import pytz
from gevent import monkey

from core.async_utils import AsyncRequests
from core.client.client import VKClient
from proxies import DEFAULT_PROXY_LIST as default_proxy_list

monkey.patch_all()


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

    def _reformat_posts(self, posts):
        format_post = FormatPost()
        for post in posts:
            if len(post) != 0:
                yield format_post.forming_post_dict(post)
            else:
                continue

    def _reformat_authors(self, posts):
        format_author = FormatAuthor()

        unique_authors = []
        for post in posts:
            if post and post.get('owner_id') not in unique_authors:
                unique_authors.append(str(post.get('owner_id')))

        client = VKClient()
        authors = client.users.get(user_ids=','.join(unique_authors))
        for author in authors['items']:
            yield format_author.forming_author_dict(author)

    def _get_authors_statistic(self, authors):
        statistic = FormatAuthor()
        for author in authors:
            yield statistic.forming_author_dict(author['items'][0], statistic=True)

    def _get_posts_statistic(self, posts):
        statistic = FormatPost()
        for post in posts:
            if len(post['items']) != 0:
                yield statistic.get_post_statistics(post['items'][0])
            else:
                continue

    def init_client_from_query(self):
        self.parameters = {
            'q': 'space',
            'count': 40,
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
            'user_ids': 'aqustics, katya_fofina, 322615035',
            'fields': 'photo_id, counters',
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        }
        self.client = VKClient(token=self.parameters['access_token'], proxy_list=self.proxy_list)

    def from_query(self):
        self.init_client_from_query()
        data = self.client.newsfeed.search(**self.parameters)
        formatted_posts = self._reformat_posts(data['items'])
        formatted_authors = self._reformat_authors(data['items'])
        return formatted_posts, formatted_authors

    def from_page(self):
        self.init_client_from_page()
        data = self.client.wall.get(**self.parameters)
        formatted_posts = self._reformat_posts(data['items'])
        return formatted_posts

    def update_posts(self):
        self.init_client_update_posts()
        data = self._fetch_data(param_key='posts', method=self.client.wall.getById)
        posts_statistic = self._get_posts_statistic(data)
        return posts_statistic

    def update_author(self):
        self.init_client_update_authors()
        data = self._fetch_data(param_key='user_ids', method=self.client.users.get)
        author_statistic = self._get_authors_statistic(data)
        return author_statistic


class DataFormatting(object):

    def generate_uid_from_string(self, astring):
        return UUID(hashlib.md5(astring.encode('utf-8')).hexdigest())

    def _get_publish_date(self, value):
        if isinstance(value, int):
            return datetime.utcfromtimestamp(value)
        raise Exception('Time value must be integer')

    def _get_thumbnail(self, content):
        max_size = 0
        url = None
        if isinstance(content, dict):
            for key, value in content.items():
                if key.startswith('photo_'):
                    size = int(key.split('_')[1])
                    if size > max_size:
                        max_size = size
                        url = value
        return url

    def _build_url(self, prefix, first_id, second_id=None):
        site_address = 'http://vk.com/'
        if second_id:
            return site_address + prefix + str(first_id) + '_' + str(second_id)
        return site_address + str(prefix) + str(first_id)

    def get_statistics(self, item):
        likes = item.get('likes', 0)
        comments = item.get('comments', 0)
        shares = item.get('reposts', 0)
        last_updated = datetime.now(pytz.utc)
        return {'likes': likes,
                'comments': comments,
                'shares': shares,
                'last_updated': last_updated}


class FormatPost(DataFormatting):

    def _get_post_type(self, item):

        ATTACHMENT_TYPES = {
            'photo': 1,
            'video': 2,
            'link': 3,
        }

        if 'attachments' in item:
            attachments = item['attachments']

            for index in xrange(len(attachments) - 1, -1, -1):
                if attachments[index]['type'] not in ATTACHMENT_TYPES:
                    attachments.pop(index)

            if attachments:
                attachment_type = attachments[0]['type']

                for attachment in attachments:
                    if attachment_type != attachment['type']:
                        return 4
                    return ATTACHMENT_TYPES[attachment_type]

        elif item.get('text'):
            return 0

    def get_post_statistics(self, post):
        statistic = self.get_statistics(post)
        post_id = 'vk_post_{}_{}'.format(post['id'], post['owner_id'])
        return {'statistic': statistic, '_id': self.generate_uid_from_string(post_id)}

    def _get_original_post(self, post):
        original_post = post['copy_history']
        return original_post

    def _get_attachments(self, item):
        attachments = {}

        for attachment in item['attachments']:
            attachment_type = attachment['type']
            attachment_content = attachment[attachment_type]
            thumbnail = self._get_thumbnail(attachment_content)
            if attachment_type == 'link':
                url = attachment_content.get('url')
            else:
                url = self._build_url(prefix=attachment_type, first_id=attachment_content['owner_id'],
                                      second_id=attachment_content['id'])

            if attachment_type not in attachments:
                attachments[attachment_type] = list()
            if url:
                attachment_dict = {'url': url}
                if thumbnail:
                    attachment_dict.update({'thumbnail': thumbnail})
                attachments[attachment_type].append(attachment_dict)

        return attachments

    def _get_vk_ids(self, item):
        post_id = str(item['id'])
        owner_id = str(item['owner_id'])
        return {'post_id': post_id, 'author_id': owner_id}

    def _get_content(self, item):
        if 'text' in item and isinstance(item, dict):
            return item.get('text')

    def forming_post_dict(self, post):
        formatted_post = {}

        if 'copy_history' in post:
            original_post = self._get_original_post(post)
            formatted_post['original_post'] = self.forming_post_dict(original_post[0])

        formatted_post['_id'] = self.generate_uid_from_string('vk_post_{}'.format(str(post['id'])))
        formatted_post['author_id'] = self.generate_uid_from_string('vk_author_{}'.format(str(post['owner_id'])))
        formatted_post['url'] = self._build_url(prefix='wall', first_id=post.get('owner_id'), second_id=post.get('id'))
        formatted_post['published_at'] = self._get_publish_date(post.get('date'))
        formatted_post['post_type'] = self._get_post_type(post)
        formatted_post['vk'] = self._get_vk_ids(post)
        formatted_post['content'] = self._get_content(post)
        formatted_post['statistic'] = self.get_statistics(post)

        if formatted_post.get('post_type') and formatted_post['post_type'] != 0:
            formatted_post.update(self._get_attachments(post))

        return formatted_post


class FormatAuthor(DataFormatting):

    def forming_author_dict(self, author, statistic=False):
        author_dict = {'_id': self.generate_uid_from_string('vk_author_{}'.format(author['id'])),
                       'vk': {'author_id': author['id']},
                       'first_name': author['first_name'],
                       'last_name': author['last_name'],
                       'url': self._build_url(prefix='id', first_id=author['id'])}
        if statistic:
            try:
                counters = author['counters']
                author_dict['statistic'] = counters
            except:
                print('For getting statistics from VK api, counters must be'
                      ' added to request fields and user page must be accessible')
        return author_dict

vk = VKData()
res = vk.from_query()

# pprint(list(res))
#
for i in res:
    for y in i:
        pprint(list(i))
