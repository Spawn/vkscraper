from core.client.request import ClientRequest, DoRequest


class VKClient(object):
    version = '5.62'

    VALID_METHODS = (
        'account',
        'apps',
        'audio',
        'auth',
        'board',
        'database',
        'docs',
        'other',
        'fave',
        'friends',
        'gifts',
        'groups',
        'likes',
        'market',
        'messages',
        'newsfeed',
        'notes',
        'notifications',
        'pages',
        'photos',
        'places',
        'polls',
        'search',
        'stats',
        'status',
        'storage',
        'users',
        'utils',
        'video',
        'wall',
        'widgets',
    )

    def __init__(self, token=None, proxy_list=None, version=version):
        self.token = token
        self._request = ClientRequest(
            api_version=version,
            token=token,
            proxy_list=proxy_list,
        )

    def __getattr__(self, item):
        if item not in self.VALID_METHODS:
            raise AttributeError('This method does not exist')

        return DoRequest(self, item)

    def pagination(self, methods, start_time=None, end_time=None, limit=None, count=100, **kwargs):
        start_item = kwargs.get('start_page', '1')
        iteration = 0
        while True:
            method, sub_method = methods

            method_obj = getattr(self, method)
            sub_method_obj = getattr(method_obj, sub_method)

            kwargs['start_from'] = start_item
            kwargs['count'] = count
            if start_time:
                kwargs['start_time'] = start_time
            if end_time:
                kwargs['end_time'] = end_time

            data = sub_method_obj(kwargs=kwargs)

            start_item = data.get('next_from')
            yield data

            if not start_item or limit and iteration >= limit:
                raise StopIteration

            iteration += 1
