import random
import requests

from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from core.client.exceptions import RequestException


class DoRequest(object):

    def __init__(self, client, chain):
        self.client = client
        self._chain = chain

    def __getattr__(self, item):
        """
        :return: Calling self with two parts VK methods.
        """

        return type(self)(self.client, self._chain + '.' + item)

    def __call__(self, *args, **kwargs):
        """
        Sends request with api method.
        """

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
        """
        Sends request to VK API and, processing API
        response and returns reformatted response.
        :param api_method: VK API method like 'wall.search'
        :param http_method: GET or POST
        :param retries:
        :param timeout:
        :param allow_redirects:
        :param proxy: List with proxy IPs
        :param kwargs:
        :return:
        """

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
        """
        Getting proxy list
        :param proxy:
        :return: random proxy IP
        """

        if proxy:
            return proxy
        elif self._proxy_list:
            return random.choice(self._proxy_list)

    def _build_url(self, method):
        params = [self.host, 'method', method]
        return '/'.join(params)
