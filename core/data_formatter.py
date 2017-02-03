import hashlib
import pytz

from datetime import datetime
from uuid import UUID


class DataFormatter(object):
    """
    Base class for formatting data which returns from VK api.
    """

    def generate_uid_from_string(self, astring):
        return UUID(hashlib.md5(astring.encode('utf-8')).hexdigest())

    def _get_publish_date(self, value):
        if isinstance(value, int):
            return datetime.utcfromtimestamp(value)
        raise Exception('Time value must be integer')

    def _get_thumbnail(self, content):
        """
        Receive content dict with thumbnails.
        Return url with max thumbnail size.
        :param content:
        :return: url
        """

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
        """
        Build the link to vk item from id.
        :param prefix:
        :param first_id:
        :param second_id:
        :return:
        """

        site_address = 'http://vk.com/'
        if second_id:
            return '{}{}{}{}{}'.format(site_address, prefix, str(first_id), '_', str(second_id))
        return '{}{}{}'.format(site_address, str(prefix), str(first_id))

    def get_statistics(self, item):
        likes = item.get('likes', 0)
        comments = item.get('comments', 0)
        shares = item.get('reposts', 0)
        last_updated = datetime.now(pytz.utc)
        return {'likes': likes,
                'comments': comments,
                'shares': shares,
                'last_updated': last_updated}


class FormatPost(DataFormatter):
    """
    Formats wall post data from VK to custom format.
    """

    ATTACHMENT_TYPES = {
        'photo': 1,
        'video': 2,
        'link': 3,
        'mixed': 4,
    }

    def _get_post_type(self, item):

        if 'attachments' in item:
            attachments = item['attachments']
            filtered_attachments = []
            for attachment in attachments:
                if attachment['type'] in self.ATTACHMENT_TYPES:
                    filtered_attachments.append(attachment)

            if filtered_attachments:
                attachment_type = filtered_attachments[0]['type']

                for attachment in filtered_attachments:
                    if attachment_type != attachment['type']:
                        return self.ATTACHMENT_TYPES['mixed']
                    return self.ATTACHMENT_TYPES[attachment_type]

        elif item.get('text'):
            return 0

    def get_post_statistics(self, post):
        statistic = self.get_statistics(post)
        post_id = 'vk_post_{}_{}'.format(post['id'], post['owner_id'])
        return {'statistic': statistic, '_id': self.generate_uid_from_string(post_id)}

    def _get_original_post(self, post):
        """
        Receive post. Returns inserted post which been shared.
        :param post:
        :return:
        """

        original_post = post['copy_history']
        return original_post

    def _get_attachments(self, item):
        """
        Receives item with data from VK api and gets
        attachments which set in ATTACHMENT_TYPES
        :param item:
        :return:
        """

        attachments = {}

        for attachment in item['attachments']:
            if attachment['type'] not in self.ATTACHMENT_TYPES:
                continue
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
        """
        Getting text data from wall post.
        :param item:
        :return:
        """

        if 'text' in item and isinstance(item, dict):
            return item.get('text')

    def as_dict(self, post):
        """
        Represents data with wall post from VK
        api to custom format and returns it as dict.
        :param post:
        :return:
        """
        formatted_post = {}

        if 'copy_history' in post:
            original_post = self._get_original_post(post)
            formatted_post['original_post'] = self.as_dict(original_post[0])

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


class FormatAuthor(DataFormatter):
    """
    Formats user profile data from VK to custom format.
    """

    def as_dict(self, author, statistic=False):
        """
        Represents data with user profile from VK
        api to custom format and returns it as dict.
        :param author:
        :param statistic: returns user statistic if True
        :return:
        """

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
