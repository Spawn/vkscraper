import gevent

from gevent import monkey

from core.async_utils import AsyncRequests
from core.client import VKClient
from core.data_formatter import FormatAuthor, FormatPost
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
                yield format_post.as_dict(post)
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
