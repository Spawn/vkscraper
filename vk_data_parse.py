import random
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter


class RequestException(Exception):
    status = 0
    error = ''

    def __init__(self, *args, **kwargs):
        super(RequestException, self).__init__(*args, **kwargs)


class DoRequest(object):

    def __init__(self, client, chain):
        self.client = client
        self._chain = chain

    def __getattr__(self, item):
        return type(self)(self.client, self._chain + '.' + item)

    def __call__(self, *args, **kwargs):
        return self.client._request(api_method=self._chain, *args, **kwargs)

    pass


class VKClient(object):
    host = 'https://api.vk.com/method/'
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

    def __init__(self, token=None, proxy_list=None):
        self.token = token
        self.proxy_list = proxy_list
        self.ua = UserAgent()

    def __getattr__(self, item):
        if item not in self.VALID_METHODS:
            raise AttributeError('This method does not exist')

        return DoRequest(self, item)

    def _request(self, api_method, http_method, allow_redirects=True, timeout=10, retries=5, **kwargs):
        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.headers.update({'User-Agent': self.ua.random})
        session.proxies.update({'http://': random.choice(self.proxy_list)})

        if self.token:
            kwargs.update({'access_token': self.token})

        method = getattr(session, http_method)

        try:
            rq_kwargs = {}
            if http_method == 'post':
                rq_kwargs['data'] = kwargs
            elif http_method == 'get':
                rq_kwargs['params'] = kwargs

            data = method(
                url=self.host + api_method,
                allow_redirects=allow_redirects,
                timeout=timeout,
                **rq_kwargs
            )

            if not data.ok:
                raise RequestException('Received no 200 status code: ' + str(data.status_code))

            if 'error' in data.text and 'error_msg' in data.text:
                raise RequestException(data.json()['error']['error_msg'])

        except requests.exceptions.RetryError:
            print 'Api resets the connection'
        except requests.exceptions.Timeout:
            print 'Api do not response'
        except requests.exceptions.RequestException as e:
            print e

        return data.json() if hasattr(data, 'json') else data

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

# client = VkClient(proxy_list=proxy_list, )
client = VKClient(proxy_list=proxy_list,
                  token='1aef5944c4ecc55630c21f9719e9c71fbae461c019926b1badd836aade794c7ee8620373f6277cde55a10',
                  )

res = client.newsfeed.search(http_method='post', owner_id=1584512, q='sun', start_time=1286668800, end_time=1296668800, count=100, start_from='222', v='5.62')

for r in res.get('response') if res.get('response') == list else (res['response']['items']):
    print r
print res['response']['next_from']



# class VKData(object):
#     def __init__(self, access_token=None):
#         self.access_token = access_token
#
#         self.client = VkClient(access_token)
#
#     def from_query(self, query, **kwargs):
#         try:
#             response = self.client.newsfeed(method='search', q=query)
#         except Exception:
#             pass
#         api_link = 'https://api.vk.com/method/newsfeed.search?q={}'.format(query)
#
#         if kwargs:
#             for arg, value in kwargs.items():
#                 api_link += "&" + arg + "=" + str(value)
#         api_link += '&' + self.access_token if self.access_token else ''
#         data = requests.request('get', api_link)
#         return json.loads(data.text).get('response')
#
#     def from_page(self, user_id, **kwargs):
#         api_link = 'https://api.vk.com/method/wall.get?{0}={1}'.format('owner_id' if type(user_id) == int else 'domain',
#                                                                        user_id)
#
#         if kwargs:
#             for arg, value in kwargs.items():
#                 api_link += "&" + arg + "=" + str(value)
#         api_link += '&' + self.access_token if self.access_token else ''
#         data = requests.request('get', api_link)
#         yield json.loads(data.text).get('response')
#
#     def update_posts(self, posts, **kwargs):
#         api_link = 'https://api.vk.com/method/wall.getById?posts='
#
#         if type(posts) == str:
#             api_link += posts
#         else:
#             api_link += ','.join([post for post in posts])
#
#         if kwargs:
#             for arg, value in kwargs.items():
#                 api_link += "&" + arg + "=" + str(value)
#         data = requests.request('get', api_link)
#         api_link += '&' + self.access_token if self.access_token else ''
#         return json.loads(data.text).get('response')
#
#     def update_user(self, user_id, fields=None, **kwargs):
#         api_link = 'https://api.vk.com/method/users.get?user_ids={}'.format(user_id)
#
#         if fields:
#             api_link += '&fields=' + ','.join([field for field in fields])
#         if kwargs:
#             for arg, value in kwargs.items():
#                 api_link += "&" + arg + "=" + str(value)
#         data = requests.request('get', api_link)
#         api_link += '&' + self.access_token if self.access_token else ''
#         return json.loads(data.text).get('response')

