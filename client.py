import json
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

        def reformat(response):
            data = response.get('response', {})
            if not isinstance(data, list):
                items = data.get('items')
                next_page = data.get('next_from')
                return {'next_from': next_page, 'items': items}
            return {'next_from': None, 'items': data}

        return reformat(data_dict)

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

    # def async_pagination(self, methods, start_time=None, end_time=None, limit=None, count=100, **kwargs):
    #     start_item = kwargs.get('start_page', '1')
    #     pages_quantity = ['']
    #     method, sub_method = methods
    #
    #     method_obj = getattr(self, method)
    #     sub_method_obj = getattr(method_obj, sub_method)
    #
    #     kwargs['start_from'] = start_item
    #     kwargs['count'] = count
    #     if start_time:
    #         kwargs['start_time'] = start_time
    #     if end_time:
    #         kwargs['end_time'] = end_time
    #
    #     def get_first():
    #         data = sub_method_obj(**kwargs)
    #
    #         pages_quantity[0] = int(data['response']['total_count'] / count)
    #         kwargs['start_from'] = count + 1
    #         return data
    #
    #     yield get_first()
    #     if int(pages_quantity[0]) > 1:
    #         monkey.patch_all()
    #         jobs = []
    #         for page in xrange(int(pages_quantity[0])):
    #             kwargs.update({'start_from': (count * page) + 1})
    #             jobs.append(gevent.spawn(sub_method_obj, **kwargs))
    #         # jobs = [gevent.spawn(sub_method_obj, kwargs=kwargs.update({'start_from': (count * page) + 1})) for page in xrange(int(pages_quantity[0]))]
    #         yield [res.get() for res in gevent.joinall(jobs)]

proxy_list = ['104.199.57.44:80',
              '104.199.93.237:80',
              '213.136.89.121:80',
              '217.33.216.114:8080',
              '104.199.30.36:80',
              '104.199.97.216:80',
              '14.199.146.171:9999',
              '104.199.35.101:80',
              '104.199.97.21:80',
              '104.199.33.19:80',
              '97.77.104.22:3128',
              '213.136.77.246:80',
              '104.199.36.105:80',
              '176.215.252.152:8080',
              '153.149.166.219:3128',
              '188.255.115.87:8080',
              '193.70.95.121:1080',
              '36.84.12.130:80',
              '36.84.12.92:80',
              '36.81.184.129:80',
              '36.84.12.99:80',
              '213.111.123.68:8080',
              '81.201.58.106:8080',
              '36.84.12.18:80',
              '36.84.12.236:80',
              '70.248.28.23:800',
              '36.84.12.195:80',
              '94.153.208.58:8080',
              '36.84.12.90:80',
              '36.84.12.6:80',
              '36.84.12.48:80',
              '36.84.12.96:80',
              '36.84.12.46:80',
              '36.84.12.76:80',
              '36.84.12.43:80',
              '36.84.12.154:80',
              '50.93.201.53:1080',
              '36.84.12.177:80',
              '36.84.12.55:80',
              '104.197.82.38:80',
              '50.93.201.28:1080',
              '36.84.12.217:80',
              '185.2.101.31:3128',
              '50.93.201.121:1080',
              '36.84.12.207:80',
              '36.84.12.246:80',
              '36.84.12.11:80',
              '36.84.12.81:80',
              '36.84.12.147:80',
              '178.73.195.162:80',
              '1.164.105.30:8998',
              '36.84.38.67:80',
              '36.84.12.156:80',
              '181.41.197.229:80',
              '77.174.132.236:80',
              '36.81.185.228:80',
              '36.81.184.101:80',
              '188.95.25.242:8080',
              '113.255.247.179:8380',
              '212.80.167.93:3128',
              '190.63.130.252:80',
              '178.161.149.18:3128',
              '36.84.12.150:80',
              '36.84.12.245:80',
              '146.120.95.1:8000',
              '14.207.153.152:8080',
              '108.170.3.139:8080',
              '194.186.82.163:8080',
              '36.84.12.7:80',
              '138.94.58.133:8080',
              '31.146.182.122:443',
              '61.91.86.134:8080',
              '70.90.16.115:8080',
              '95.83.60.251:8080',
              '31.135.91.13:8081',
              '125.167.254.126:8080',
              '176.31.175.213:4444',
              '222.98.44.125:3128',
              '203.144.137.194:8080',
              '103.18.180.5:8080',
              '66.122.95.218:8080',
              '220.143.198.176:3128',
              '182.253.152.7:8080',
              '36.76.183.227:3128',
              '119.40.98.162:8080',
              '54.232.232.250:60088',
              '41.77.184.36:8080',
              '139.255.40.130:8080',
              '182.253.177.134:8080',
              '43.245.141.214:8080',
              '213.131.45.250:8080',
              '46.216.188.183:8081',
              '119.93.88.154:3128',
              '36.67.25.122:8080',
              '180.245.91.244:80',
              '37.145.155.19:9999',
              '103.18.180.94:8080',
              '181.215.158.86:8080',
              '50.93.202.36:1080',
              '47.88.107.60:80',
              '195.138.86.112:3128',
              '175.144.119.244:80',
              '182.253.37.230:3128',
              '110.232.255.161:8080',
              '77.241.31.126:8080',
              '114.199.125.242:8080',
              '118.172.56.240:8080',
              '36.81.255.73:8080',
              '203.142.76.90:8080',
              '183.91.87.39:3128',
              '144.217.185.22:80',
              '203.172.232.13:8080',
              '31.131.67.76:8080',
              '125.160.54.19:8080',
              '47.88.195.204:80',
              '36.84.12.200:80',
              '36.84.12.44:80',
              '36.84.12.187:80',
              '47.90.74.111:8088',
              '185.28.193.95:8080',
              '36.84.12.105:80',
              '36.84.12.202:80',
              '36.81.185.101:80',
              '36.81.185.9:80',
              '36.81.185.91:80',
              '36.81.185.96:80',
              '36.81.184.37:80',
              '203.172.228.69:8080',
              '36.81.185.56:80',
              '154.72.185.50:80',
              '36.84.12.158:80',
              '36.84.12.22:80',
              '36.81.185.8:80',
              '52.53.160.7:80',
              '101.96.104.93:8080',
              '179.106.71.2:8080',
              '36.84.12.30:80',
              '36.84.12.103:80',
              '36.84.12.167:80',
              '36.84.12.198:80',
              '36.84.12.102:80',
              '54.232.231.237:60088',
              '36.84.12.204:80',
              '91.217.34.137:8080',
              '36.84.12.86:80',
              '36.84.12.234:80',
              '182.93.241.198:8080',
              '104.199.23.24:80',
              '68.230.52.88:21320',
              '36.84.12.67:80',
              '36.84.12.117:80',
              '46.146.220.74:8080',
              '36.84.12.47:80',
              '36.84.12.4:80',
              '36.84.12.224:80',
              '180.254.45.88:80',
              '36.84.12.95:80',
              '61.193.73.105:8000',
              '5.189.162.211:3128',
              '47.89.41.164:80',
              '36.81.184.154:80',
              '50.93.203.31:1080',
              '205.234.15.12:80',
              '36.82.72.104:80',
              '36.81.185.138:80',
              '36.81.184.171:80',
              '41.87.64.210:8080',
              '36.81.184.46:80',
              '192.129.229.89:9001',
              '36.81.184.23:80',
              '104.236.55.48:8080',
              '178.218.113.2:8080',
              '54.232.240.30:60088',
              '36.84.12.194:80',
              '202.152.154.46:8080',
              '5.152.233.1:8080',
              '88.199.164.135:8080',
              '45.248.146.70:8080',
              '36.66.35.202:3128',
              '31.162.141.212:8080',
              '192.140.223.94:8080',
              '36.76.83.48:8080',
              '183.91.87.36:3128',
              '36.84.12.174:80',
              '95.128.227.40:8080',
              '54.235.115.76:80',
              '36.84.12.10:80',
              '192.169.168.151:8888',
              '36.84.12.14:80',
              '36.84.12.235:80',
              '5.2.73.231:1080',
              '36.84.12.152:80',
              '36.84.12.70:80',
              '36.84.12.218:80',
              '36.84.12.34:80',
              '36.84.12.157:80',
              '163.121.188.3:8080',
              '36.84.12.83:80',
              '66.23.227.52:1080',
              '188.166.144.251:8118',
              '36.84.12.186:80',
              '138.68.130.94:8118',
              '91.201.40.22:4444',
              '41.33.180.107:8080',
              '5.2.69.165:1080',
              '190.192.19.237:8080',
              '182.253.244.21:8080',
              '200.33.128.94:8080',
              '208.65.66.130:8080',
              '45.248.146.33:8080',
              '114.31.4.18:8080',
              '202.58.111.26:8080',
              '58.84.15.241:8080',
              '197.231.202.19:8080',
              '103.26.247.134:8080',
              '103.229.86.88:8080',
              '193.179.1.114:8080',
              '124.40.246.193:8080',
              '103.4.165.244:8080',
              '43.250.227.94:8080',
              '110.36.217.158:8080',
              '154.73.46.81:8080',
              '94.102.124.56:8080',
              '85.199.71.125:8080',
              '110.78.164.8:8080',
              '202.136.89.137:8080',
              '77.241.18.10:8080',
              '188.169.123.210:8080',
              '159.224.144.135:8080',
              '179.108.39.193:8080',
              '109.120.246.244:8080',
              '179.108.42.31:8080',
              '178.62.127.13:8080',
              '110.164.93.42:8080',
              '203.124.47.210:8080',
              '103.52.134.130:8080',
              '138.204.68.58:8080',
              '94.142.142.140:3128',
              '5.40.175.119:8082',
              '175.101.8.46:8090',
              '177.128.224.254:8080',
              '81.22.190.254:8080',
              '88.199.164.134:8080',
              '93.100.160.53:8081',
              '101.109.253.80:8080',
              '84.22.35.37:3129',
              '154.73.46.69:8080',
              '92.241.75.194:8080',
              '179.108.42.1:8080',
              '95.171.198.206:8080',
              '210.57.215.13:3128',
              '197.210.185.186:8080',
              '146.88.71.67:8080',
              '83.171.102.171:8081',
              '161.0.188.2:3128',
              '182.253.26.246:8080',
              '199.195.119.37:80',
              '103.18.80.1:8080',
              '195.9.237.38:8080',
              '189.112.22.151:8080',
              '202.58.111.34:8080',
              '103.254.27.18:8088',
              '154.73.44.41:8080',
              '220.134.98.192:8088',
              '46.243.178.254:8888',
              '107.180.75.19:80',
              '117.121.204.238:31281',
              '51.255.128.46:3128',
              '36.81.184.9:80',
              '36.84.12.45:80',
              '36.84.12.137:80',
              '36.84.12.229:80',
              '5.40.175.161:8082',
              '136.243.82.159:8118',
              '45.248.146.49:8080',
              '210.68.95.62:3128',
              '209.150.146.28:8080',
              '31.146.81.82:8080',
              '5.228.39.182:8081',
              '110.232.255.177:8080',
              '217.17.163.71:8118',
              '93.139.139.238:8080',
              '188.56.26.113:8080',
              '139.193.134.18:8080',
              '125.62.197.49:8080',
              '113.53.177.49:8080',
              '42.112.210.232:49132',
              '176.239.79.125:8080',
              '163.172.177.87:3128',
              '94.125.189.194:8080',
              '119.14.79.27:80',
              '36.232.127.91:3128',
              '1.20.181.2:8080',
              '94.124.195.233:8080',
              '190.237.139.234:8080',
              '46.16.226.10:8080',
              '190.74.255.107:8080',
              '93.183.76.104:8080',
              '45.115.173.26:8080',
              '41.79.137.239:8080',]
