from app import VKFromQuery, VKFromPage, VKUpdateAuthors, VKUpdatePosts

CONF = {
    'vk': {
        'modules': {
            'from.query': VKFromQuery,
            'from.page': VKFromPage,
            'update.authors': VKUpdateAuthors,
            'update.posts': VKUpdatePosts,
        }
    }
}
