#!/usr/bin/env python
import pika, pika.spec as ps
import json

smol = {
    "name":"llo",
    "title": "yolo"
}
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost',5672,'youtuberservice',pika.PlainCredentials('youtuber','youtuber')))
channel = connection.channel()

channel.queue_declare(queue='upload_video')
channel.confirm_delivery()

channel.basic_publish(exchange='', routing_key='upload_video', body=json.dumps(smol),properties=pika.BasicProperties(delivery_mode=2),mandatory=True)
print(" [x] Sent ",smol)

connection.close()
