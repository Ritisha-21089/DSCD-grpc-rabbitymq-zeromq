import os, sys
import pika, pika.spec as ps
import json

argv = sys.argv[1:]
argc = len(argv)

class Youtuber:
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
            self.channel.queue_declare(queue='upload_video')
            self.channel.confirm_delivery()
            return True
        except:
            print("Failed to establish connection")
            return False
        

    def publish_video(self,name,title):
        d = json.dumps({"name":name, "title":title})
        try: 
            self.channel.basic_publish(
                exchange='',
                routing_key='upload_video', 
                body=d,properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True
                )
            print(f"SUCCESS")
            return True
        except:
            print("FAILIURE")
            return False
        
    
    def stop(self):
        try:
            self.connection.close()
            return True
        except:
            print("connection already closed")
            return False
        
if(argc > 2):
    print("Too Many Arguments")
    sys.exit(1)
elif( argc < 2):
    print("Insufficient Argument")
    sys.exit(1)
else:
    y = Youtuber()
    if(y.start()):
        y.publish_video(argv[0],argv[1])
        y.stop()