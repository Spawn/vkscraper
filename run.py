from pprint import pprint

from app import VKData

vk = VKData()
res = vk.from_query()

# pprint(list(res))
#
for i in res:
    for y in i:
        pprint(list(i))
