import random
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter


class RequestException(Exception):
    pass


class DoRequest(object):
    def __init__(self, client, chain):
        self.client = client
        self._chain = chain

    def __getattr__(self, item):
        return type(self)(self.client, self._chain + '.' + item)

    def __call__(self, *args, **kwargs):
        return self.client._request.send(api_method=self._chain, *args, **kwargs)


class ClientRequest(object):
    host = 'https://api.vk.com'

    def __init__(self, token=None, proxy_list=None, api_version=None):
        self._token = token
        self._proxy_list = proxy_list
        self._user_agent = UserAgent()
        self.version = api_version

    def _build_session(self, retries=5, proxy=None):
        proxy_url = self._get_proxy(proxy)

        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.headers.update({'User-Agent': self._user_agent.random})
        session.proxies.update({'http://': proxy_url})

        return session

    def send(self, api_method, http_method='get', retries=5, timeout=10, allow_redirects=True, proxy=None, **kwargs):

        if 'v' not in kwargs:
            kwargs['v'] = self.version

        session = self._build_session(retries=retries, proxy=proxy)
        method = getattr(session, http_method)

        rq_kwargs = {}
        if http_method == 'post':
            rq_kwargs['data'] = kwargs
        elif http_method == 'get':
            rq_kwargs['params'] = kwargs
        else:
            raise ValueError('HTTP method not allowed')

        data = method(
            url=self._build_url(method=api_method),
            allow_redirects=allow_redirects,
            timeout=timeout,
            **rq_kwargs
        )

        if not data.ok:
            raise RequestException('Received no 200 status code: ' + str(data.status_code))

        data_dict = data.json()

        if 'error' in data_dict and 'error_msg' in data_dict['error']:
            raise RequestException(data_dict['error']['error_msg'])

        def reformat(response):
            data = response.get('response', {})
            if not isinstance(data, list):
                items = data.get('items')
                next_page = data.get('next_from')
                return {'next_from': next_page, 'items': items}
            return {'next_from': None, 'items': data}

        return reformat(response=data_dict)

    def _get_proxy(self, proxy=None):
        if proxy:
            return proxy
        elif self._proxy_list:
            return random.choice(self._proxy_list)

    def _build_url(self, method):
        params = [self.host, 'method', method]
        return '/'.join(params)


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

    # def get_data_range(self, api_method, *args, **kwargs):
    #     start_item = kwargs.get('start_page', '1')
    #     while True:
    #         kwargs['start_from'] = start_item
    #         data = self._request.send(api_method=api_method, *args, **kwargs)
    #         start_item = data.get('response').get('next_from')
    #         if isinstance(data.get('response'), list):
    #             items = data.get('response')
    #         else:
    #             items = data.get('response').get('items')
    #         yield items
    #         if not start_item:
    #             raise StopIteration()

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

            data = sub_method_obj(**kwargs)

            start_item = data.get('next_from')

            if not start_item or limit and iteration >= limit:
                raise StopIteration

            iteration += 1
            yield data


proxy_list = ['36.81.184.111:80',
              '70.248.28.23:800',
              '36.81.185.56:80',
              '104.199.117.203:80',
              '36.81.185.136:80',
              '104.196.233.61:80',
              '139.59.44.124:80',
              '97.77.104.22:3128',
              '122.129.74.147:8080',
              '103.52.134.97:8080',
              '110.164.58.147:9001',
              '36.81.184.192:80',
              '36.81.215.176:80',
              '191.252.100.77:8080',
              '63.128.95.200:8888',
              '36.81.185.29:80',
              '196.196.2.12:1080',
              '45.76.130.31:3128',
              '212.220.10.243:8080',
              '196.196.2.4:1080',
              '196.196.2.21:1080',
              '196.196.2.8:1080',
              '36.81.185.1:80',
              '35.185.8.144:80',
              '104.199.121.181:80',
              '36.81.184.129:80',
              '213.136.89.121:80',
              '213.136.77.246:80',
              '36.84.12.163:80',
              '36.81.184.23:80',
              '217.33.216.114:8080',
              '93.142.19.60:8080',
              '45.76.137.247:3128',
              '36.84.12.23:80',
              '36.84.12.142:80',
              '178.62.95.209:8118',
              '182.52.233.40:8080',
              '195.9.237.66:8080',
              '187.76.192.130:8080',
              '188.32.79.247:8081',
              '203.128.17.1:8080',
              '179.235.208.38:8080',
              '197.210.252.39:8080',
              '12.33.254.195:3128',
              '36.82.73.57:80',
              '37.72.185.34:1080',
              '47.90.74.111:8088',
              '37.72.185.2:1080',
              '37.72.185.3:1080',
              '178.161.149.18:3128',
              '47.89.41.164:80',
              '36.82.127.41:80',
              '36.81.184.119:80',
              '37.72.185.4:1080',
              '37.29.83.228:8080',
              '36.81.185.130:80',
              '93.175.29.101:2222',
              '188.170.211.206:8080',
              '36.81.184.171:80',
              '36.84.12.57:80',
              '95.31.3.34:8080',
              '36.81.184.46:80',
              '36.81.185.79:80',
              '23.24.89.194:7004',
              '36.81.185.233:80',
              '165.84.188.67:80',
              '36.84.12.212:80',
              '36.84.12.61:80',
              '36.84.12.47:80',
              '36.84.12.152:80',
              '36.84.12.217:80',
              '36.84.12.99:80',
              '36.84.12.196:80',
              '36.84.12.210:80',
              '36.84.12.33:80',
              '36.84.12.37:80',
              '36.81.185.3:80',
              '36.84.12.103:80',
              '37.72.185.43:1080',
              '37.29.83.212:8080']

client = VKClient(proxy_list=proxy_list,
                  # token='2bf85846cadb59da0b8f36cf7fef3d19b2fd469edd9bebe45643238c50fad568d1f2a496c9d8f1de602f7',
                  )

# res = client.newsfeed.search(http_method='post', q='wawe', count=100)

# print len(res)

test = client.pagination(('newsfeed', 'search'), q='city')

print len(list(test))
