import os, sys
import pika, pika.spec as ps
import json

argv = sys.argv[1:]
argc = len(argv)


class User:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def start(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    'localhost',
                    5672,
                    'youtuberservice'
                    ,pika.PlainCredentials('youtuber','youtuber')
                    )
                )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='subscription')
            self.channel.confirm_delivery()

            self.notif = self.connection.channel()
            return True
        except:
            print("Failed to establish connection")
            return False
    
    def update_subscription(self,submode,name,youtuber):
        d = json.dumps({"name":name, "youtuber":youtuber,"subscription":submode})
        try: 
            self.channel.basic_publish(
                exchange='',
                routing_key='subscription', 
                body=d,properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True
                )
            print(f"SUCCESS")
            return True
        except:
            print("FAILIURE")
            return False
    
    def recieve_notification(self,name):
        self.notif.queue_declare(queue=name)
        self.notif.basic_consume(queue=name, on_message_callback=self.callback, auto_ack=True)
        self.notif.start_consuming()
        
    def callback(self, ch, method, properties, body):
        print(body)

u = User()
u.start()
if argc == 1:
    u.recieve_notification(argv[0])
elif argc == 3:
    if(argv[1] == "s"):
        u.update_subscription("true",argv[0],argv[2])
    elif ((argv[1] == "u")):
        u.update_subscription("false",argv[0],argv[2])
    else:
        print("invalid argument")
else:
    print("invalid argument")