import requests
import json


class VKData(object):
    def __init__(self, access_token=None):
        self.access_token = access_token

    def from_query(self, query, **kwargs):
        api_link = 'https://api.vk.com/method/newsfeed.search?q={}'.format(query)

        if kwargs:
            for arg, value in kwargs.items():
                api_link += "&" + arg + "=" + str(value)
        api_link += '&' + self.access_token if self.access_token else ''
        data = requests.request('get', api_link)
        return json.loads(data.text).get('response')

    def from_page(self, user_id, **kwargs):
        api_link = 'https://api.vk.com/method/wall.get?{0}={1}'.format('owner_id' if type(user_id) == int else 'domain', user_id)

        if kwargs:
            for arg, value in kwargs.items():
                api_link += "&" + arg + "=" + str(value)
        api_link += '&' + self.access_token if self.access_token else ''
        data = requests.request('get', api_link)
        return json.loads(data.text).get('response')

    def update_posts(self, posts, **kwargs):
        api_link = 'https://api.vk.com/method/wall.getById?posts='

        if type(posts) == str:
            api_link += posts
        else:
            api_link += ','.join([post for post in posts])

        if kwargs:
            for arg, value in kwargs.items():
                api_link += "&" + arg + "=" + str(value)
        data = requests.request('get', api_link)
        api_link += '&' + self.access_token if self.access_token else ''
        return json.loads(data.text).get('response')

    def update_user(self, user_id, fields=None, **kwargs):
        api_link = 'https://api.vk.com/method/users.get?user_ids={}'.format(user_id)

        if fields:
            api_link += '&fields=' + ','.join([field for field in fields])
        if kwargs:
            for arg, value in kwargs.items():
                api_link += "&" + arg + "=" + str(value)
        data = requests.request('get', api_link)
        api_link += '&' + self.access_token if self.access_token else ''
        return json.loads(data.text).get('response')

client = VKData(access_token='0rWPHYHKBJ2lVBWwaal2')

print client.from_page(user_id=15723625, count=2)
