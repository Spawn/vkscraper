import json

import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='from.query',
                         type='topic')

routing_key = '#'
message = json.dumps({
            'q': 'space',
            'count': 40,
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        })
channel.basic_publish(exchange='from.query',
                      routing_key=routing_key,
                      body=message)

message = json.dumps({
            'owner_id': 15723625,
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        })

channel.basic_publish(exchange='from.page',
                      routing_key=routing_key,
                      body=message)

message = json.dumps({
            'posts': '15723625_5801, 15723625_5800,15723625_5799,15723625_5798,15723625_5797,\
            15723625_5796,15723625_5795,15723625_5794,15723625_5793, 15723625_5792,15723625_5791,\
            15723625_5790,15723625_5789,15723625_5788,15723625_5787,15723625_5786,15723625_5784,\
            15723625_5783,15723625_5782,43291122_33348,15723625_5806,15723625_5808,15723625_5809',
            'access_token': '',
            'extended': '1',
        })

channel.basic_publish(exchange='update.posts',
                      routing_key=routing_key,
                      body=message)

message = json.dumps({
            'user_ids': 'aqustics, katya_fofina, 322615035',
            'fields': 'photo_id, counters',
            'access_token': '2d81c89832f2226c7b848eb0306b3a1219096a1faef6ab9969e99bd9bd5b640c2617edb6d2b165ac05533',
        })

channel.basic_publish(exchange='update.authors',
                      routing_key=routing_key,
                      body=message)

connection.close()
