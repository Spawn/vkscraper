import inspect
import random
from fake_useragent import UserAgent
import requests
import urllib

PROXIES = ['36.81.184.111:80', '70.248.28.23:800', '36.81.185.56:80', '104.199.117.203:80', '36.81.185.136:80', '104.196.233.61:80', '139.59.44.124:80', '97.77.104.22:3128', '122.129.74.147:8080', '103.52.134.97:8080', '110.164.58.147:9001', '36.81.184.192:80', '36.81.215.176:80', '191.252.100.77:8080', '63.128.95.200:8888', '36.81.185.29:80', '196.196.2.12:1080', '45.76.130.31:3128', '212.220.10.243:8080', '196.196.2.4:1080', '196.196.2.21:1080', '196.196.2.8:1080', '36.81.185.1:80', '35.185.8.144:80', '104.199.121.181:80', '36.81.184.129:80', '213.136.89.121:80', '213.136.77.246:80', '36.84.12.163:80', '36.81.184.23:80', '217.33.216.114:8080', '93.142.19.60:8080', '45.76.137.247:3128', '36.84.12.23:80', '36.84.12.142:80', '178.62.95.209:8118', '182.52.233.40:8080', '195.9.237.66:8080', '187.76.192.130:8080', '188.32.79.247:8081', '203.128.17.1:8080', '179.235.208.38:8080', '197.210.252.39:8080', '12.33.254.195:3128', '36.82.73.57:80', '37.72.185.34:1080', '47.90.74.111:8088', '37.72.185.2:1080', '37.72.185.3:1080', '178.161.149.18:3128', '47.89.41.164:80', '36.82.127.41:80', '36.81.184.119:80', '37.72.185.4:1080', '37.29.83.228:8080', '36.81.185.130:80', '93.175.29.101:2222', '188.170.211.206:8080', '36.81.184.171:80', '36.84.12.57:80', '95.31.3.34:8080', '36.81.184.46:80', '36.81.185.79:80', '23.24.89.194:7004', '36.81.185.233:80', '165.84.188.67:80', '36.84.12.212:80', '36.84.12.61:80', '36.84.12.47:80', '36.84.12.152:80', '36.84.12.217:80', '36.84.12.99:80', '36.84.12.196:80', '36.84.12.210:80', '36.84.12.33:80', '36.84.12.37:80', '36.81.185.3:80', '36.84.12.103:80', '37.72.185.43:1080', '37.29.83.212:8080']


class RequestException(Exception):
    status = 0
    error = ''

    def __init__(self, *args, **kwargs):
        super(RequestException, self).__init__(*args, **kwargs)


class VkClient(object):
    host = 'https://api.vk.com/method/'

    def __init__(self, token=None):
        self.token = token
        self.ua = UserAgent()

    def _request(self, method, args):
        args.update({'access_token': self.token}) if self.token else None
        str_args = urllib.urlencode(args)
        url = self.host + inspect.stack()[1][3] + '.' + method + '?' + str_args
        data = requests.get(url, proxies={'http://': random.choice(PROXIES)}, headers={'User-Agent': self.ua.random}).json()

        if data.get('error', ''):
            raise RequestException(data.get('error').get('error_msg'))

        return data

    def account(self, method, **kwargs):
        return self._request(method, kwargs)

    def apps(self, method, **kwargs):
        return self._request(method, kwargs)

    def audio(self, method, **kwargs):
        return self._request(method, kwargs)

    def auth(self, method, **kwargs):
        return self._request(method, kwargs)

    def board(self, method, **kwargs):
        return self._request(method, kwargs)

    def database(self, method, **kwargs):
        return self._request(method, kwargs)

    def docs(self, method, **kwargs):
        return self._request(method, kwargs)

    def other(self, method, **kwargs):
        return self._request(method, kwargs)

    def fave(self, method, **kwargs):
        return self._request(method, kwargs)

    def friends(self, method, **kwargs):
        return self._request(method, kwargs)

    def gifts(self, method, **kwargs):
        return self._request(method, kwargs)

    def groups(self, method, **kwargs):
        return self._request(method, kwargs)

    def likes(self, method, **kwargs):
        return self._request(method, kwargs)

    def market(self, method, **kwargs):
        return self._request(method, kwargs)

    def messages(self, method, **kwargs):
        return self._request(method, kwargs)

    def newsfeed(self, method, **kwargs):
        return self._request(method, kwargs)

    def notes(self, method, **kwargs):
        return self._request(method, kwargs)

    def notifications(self, method, **kwargs):
        return self._request(method, kwargs)

    def pages(self, method, **kwargs):
        return self._request(method, kwargs)

    def photos(self, method, **kwargs):
        return self._request(method, kwargs)

    def places(self, method, **kwargs):
        return self._request(method, kwargs)

    def polls(self, method, **kwargs):
        return self._request(method, kwargs)

    def search(self, method, **kwargs):
        return self._request(method, kwargs)

    def stats(self, method, **kwargs):
        return self._request(method, kwargs)

    def status(self, method, **kwargs):
        return self._request(method, kwargs)

    def storage(self, method, **kwargs):
        return self._request(method, kwargs)

    def users(self, method, **kwargs):
        return self._request(method, kwargs)

    def utils(self, method, **kwargs):
        return self._request(method, kwargs)

    def video(self, method, **kwargs):
        return self._request(method, kwargs)

    def wall(self, method, **kwargs):
        return self._request(method, kwargs)

    def widgets(self, method, **kwargs):
        return self._request(method, kwargs)


client = VkClient()
# client = VkClient(token='40d31b3c7c18ef58888d070e6ff28bf26efddedd2ca08d4db9295d685167de9638f387d15a9d1e42f64ed')

for i in xrange(100):
    print client.users('get', user_ids='aqustics', fields='sex, city, bdate, counters')










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

