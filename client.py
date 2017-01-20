import random
from pprint import pprint

import gevent
import requests
from fake_useragent import UserAgent
from gevent import monkey
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
        if self._token:
            kwargs['access_token'] = self._token

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

        # def reformat(response):
        #     data = response.get('response', {})
        #     if not isinstance(data, list):
        #         items = data.get('items')
        #         next_page = data.get('next_from')
        #         return {'next_from': next_page, 'items': items}
        #     return {'next_from': None, 'items': data}

        return data_dict

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

    def async_pagination(self, methods, start_time=None, end_time=None, limit=None, count=100, **kwargs):
        start_item = kwargs.get('start_page', '1')
        pages_quantity = ['']
        method, sub_method = methods

        method_obj = getattr(self, method)
        sub_method_obj = getattr(method_obj, sub_method)

        kwargs['start_from'] = start_item
        kwargs['count'] = count
        if start_time:
            kwargs['start_time'] = start_time
        if end_time:
            kwargs['end_time'] = end_time

        def get_first():
            data = sub_method_obj(**kwargs)

            pages_quantity[0] = int(data['response']['total_count'] / count)
            return data

        yield get_first()
        if int(pages_quantity[0]) > 1:
            monkey.patch_all()
            jobs = [gevent.spawn(sub_method_obj, kwargs=kwargs.update({'start_from': page + count})) for page in xrange(int(pages_quantity[0]))]
            yield [res.get() for res in gevent.joinall(jobs)]

proxy_list = ['94.181.119.66:8080',
              '36.84.12.224:80',
              '36.84.12.58:80',
              '5.189.162.211:3128',
              '36.84.12.192:80',
              '36.84.12.162:80',
              '36.84.12.82:80',
              '36.84.12.56:80',
              '36.84.12.127:80',
              '36.84.12.166:80',
              '97.77.104.22:3128',
              '36.84.12.100:80',
              '5.2.73.231:1080',
              '36.84.12.177:80',
              '200.145.221.20:80',
              '36.84.12.24:80',
              '36.84.12.145:80',
              '138.201.63.122:31288',
              '104.154.142.106:3128',
              '36.84.12.173:80',
              '36.84.12.179:80',
              '36.84.12.197:80',
              '36.84.12.51:80',
              '36.84.12.86:80',
              '213.136.77.246:80',
              '213.136.89.121:80',
              '36.84.12.13:80',
              '36.84.12.248:80',
              '153.149.166.219:3128',
              '36.84.12.32:80',
              '36.84.12.18:80',
              '70.248.28.23:800',
              '52.211.214.122:8080',
              '36.84.12.176:80',
              '36.85.56.116:80',
              '5.45.64.97:3128',
              '36.84.12.46:80',
              '36.84.12.199:80',
              '36.84.12.157:80',
              '36.84.12.61:80',
              '36.84.12.169:80',
              '36.84.12.150:80',
              '36.84.12.168:80',
              '36.84.12.200:80',
              '36.84.12.95:80',
              '36.84.12.148:80',
              '36.84.12.36:80',
              '36.84.12.231:80',
              '36.84.12.5:80',
              '36.84.12.45:80',
              '36.84.12.167:80',
              '36.84.12.30:80',
              '51.255.128.46:3128',
              '36.84.12.112:80',
              '36.84.12.207:80',
              '62.183.42.141:8080',
              '36.84.12.195:80',
              '36.84.12.8:80',
              '36.84.12.77:80',
              '36.84.12.202:80',
              '36.84.12.49:80',
              '36.84.12.38:80',
              '185.28.193.95:8080',
              '12.33.254.195:3128',
              '36.84.12.147:80',
              '36.84.12.212:80',
              '36.84.12.158:80',
              '36.84.12.234:80',
              '36.84.12.67:80',
              '36.84.12.89:80',
              '36.84.12.65:80',
              '36.84.12.42:80'
              '36.84.12.210:80',
              '36.84.12.221:80',
              '13.88.183.184:3128',
              '36.84.12.102:80',
              '36.84.12.137:80'
              '36.84.12.66:80',
              '36.84.12.70:80',
              '36.84.12.10:80',
              '36.84.12.82:80',
              '83.239.58.162:8080',
              '36.84.12.84:80',
              '36.84.12.148:80',
              '13.88.183.184:3128',
              '45.32.103.220:3128',
              '36.84.12.23:80',
              '138.201.63.122:31288',
              '104.154.142.106:3128',
              '70.248.28.23:800',
              '153.149.166.219:3128',
              '213.136.89.121:80',
              '213.136.77.246:80',
              '97.77.104.22:3128',
              '149.56.142.212:8080',
              '69.12.78.178:1080',
              '151.80.88.44:3128',
              '52.211.214.122:8080',
              '36.84.12.139:80',
              '111.68.30.182:8080',
              '36.84.12.145:80',
              '109.111.227.221:6666',
              '178.140.152.211:8081',
              '36.66.124.215:8080',
              '103.56.30.78:8080',
              '170.239.46.74:8080',
              '46.16.226.10:8080',
              '5.40.175.107:8082',
              '5.40.175.123:8082',
              '186.226.253.254:3128',
              '103.18.80.1:8080',
              '197.32.156.60:8080',
              '176.111.83.137:8080',
              '80.188.135.12:8080',
              '36.79.186.213:8080',
              '108.93.5.220:3128',
              '91.98.31.164:8080',
              '43.252.199.105:8080',
              '190.63.155.146:8080',
              '88.199.18.47:8090',
              '213.24.57.238:8080',
              '220.128.77.116:8080',
              '223.196.70.6:8080',
              '192.129.232.143:9001',
              '62.176.5.93:8080',
              '5.2.69.176:1080',
              '187.69.236.201:8080',
              '80.245.117.133:8080',
              '159.255.167.131:8080',
              '187.16.43.49:8080',
              '41.33.180.107:8080',
              '159.192.248.67:8080',
              '113.252.67.119:8088',
              '91.93.73.235:8080',
              '92.45.51.209:9999',
              '186.117.128.92:8080',
              '202.71.24.25:8080',
              '176.32.129.192:8080',
              '91.98.31.165:8080',
              '212.2.230.110:8080',
              '181.211.191.227:8080',
              '95.215.52.150:8080',
              '179.108.164.121:8080',
              '91.98.31.163:8080',
              '178.19.98.1:8088',
              '202.58.111.26:8080',
              '5.57.58.230:80',
              '188.162.171.214:8081',
              '41.221.76.9:8080',
              '179.243.2.223:8080',
              '138.255.100.47:8080',
              '2.94.40.164:8080',
              '132.148.70.128:80',
              '181.224.253.162:8081',
              '178.140.12.69:8081',
              '192.129.226.71:9001',
              '163.47.147.34:8080',
              '85.194.75.18:8080',
              '183.89.144.176:8080',
              '187.69.9.117:8080']

client = VKClient(
    proxy_list=proxy_list,
    # token='2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
)


test = client.async_pagination(('newsfeed', 'search'), q='azazazaz')
for item in test:
    pprint(item)
