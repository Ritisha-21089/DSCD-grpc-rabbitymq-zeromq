import pika,pika.spec as ps
import json, sys, pika.channel
import threading
import functools

class Server_P:
    def __init__(self):
        self.user_ch = None
        self.notif_ch = None
        self.youtuber_ch = None
        
        self.youtuber_con = None
        self.user_exchange_nt = None
    
    def consume_youtuber(self, _unused_channel, method, properties, body):
        p_body = json.loads(body)
        if "name" in p_body.keys() and "title" in p_body.keys():
            self.youtuber_ch.basic_ack(delivery_tag=method.delivery_tag)
            self.notify_user(p_body["name"], p_body["title"])
            # print(body)
        else:
            self.youtuber_ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
            print("failed")
    
    def consume_user(self, _unused_channel, method, properties, body):
        p_body = json.loads(body)
        if "name" in p_body.keys() and "subscription" in p_body.keys() and "youtuber" in p_body.keys():
            self.user_ch.basic_ack(delivery_tag=method.delivery_tag)
            cb = functools.partial(self.us_queue_bind, userdata=p_body)
            self.user_ch.queue_declare(queue=p_body["name"],callback=cb)
            # print(body)
        else:
            self.user_ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
            print("failed")
    
    def notify_user(self,name,title):
        print("Notifying users subscribed to ",name)
        self.notif_ch.basic_publish(self.user_exchange_nt,name,name + " uploaded " + title)

    def us_queue_bind(self,channel,userdata):
        if(userdata["subscription"]) == "true":
            print(f"binded queue of",userdata["name"],userdata["youtuber"])
            self.user_ch.queue_bind(
                userdata["name"],
                self.user_exchange_nt,
                routing_key=userdata["youtuber"],
                )
        else:
            print(f"unbinded queue of, probabaly")
            self.user_ch.queue_unbind(
                userdata["name"],
                self.user_exchange_nt,
                routing_key=userdata["youtuber"],
            )

    def start(self):
        self.youtuber_con = pika.SelectConnection(
            parameters=pika.ConnectionParameters('localhost',5672,'youtuberservice',pika.PlainCredentials('server','server')),
            on_open_callback=self.yt_on_connection_open,
            on_open_error_callback=self.yt_on_connection_open_error,
            on_close_callback=self.yt_on_connection_closed
            )

        self.youtuber_con.ioloop.start()
    
    def stop(self):
        if(self.youtuber_con):
            self.youtuber_con.ioloop.stop()
        print("Stopped")

    def yt_on_connection_open(self,connection):
        print("connection established to youtuber-service")
        self.youtuber_con.channel(on_open_callback=self.us_on_channel_open)

    def yt_on_connection_open_error(self,connection,err):
        print("connection failed to youtuber-service: ",err)

    def yt_on_connection_closed(self,_,res):
        print("youtuber connection is or was closed,",res)

    def us_on_channel_open(self, channel: pika.channel.Channel):
        print("channel opened for youtubers")
        self.user_ch = channel
        self.youtuber_con.channel(on_open_callback=self.nt_on_channel_open)

    def nt_on_channel_open(self, channel: pika.channel.Channel):
        print("channel opened for youtubers")
        self.notif_ch = channel
        self.youtuber_con.channel(on_open_callback=self.yt_on_channel_open)

    def yt_on_channel_open(self, channel: pika.channel.Channel):
        print("channel opened for youtubers")
        self.youtuber_ch = channel
        self.user_exchange_nt = "connector"
        self.notif_ch.exchange_declare(
            exchange="connector",
            exchange_type="direct",
            callback=self.nt_on_exchange_declareok)

    def nt_on_exchange_declareok(self,_):
        print("Exchange declared")
        self.youtuber_ch.add_on_close_callback(self.yt_on_channel_closed)
        self.user_ch.add_on_close_callback(self.us_on_channel_closed)
        self.notif_ch.add_on_close_callback(self.nt_on_channel_closed)
        self.youtuber_ch.queue_declare(queue="upload_video", callback=self.yt_on_queue_declareok)
        self.user_ch.queue_declare(queue="subscription", callback=self.us_on_queue_declareok)

    def us_on_queue_declareok(self,_):
        self.user_ch.add_on_cancel_callback(self.us_on_consumer_cancelled)
        self.user_ch.basic_consume(
            "subscription", self.consume_user)
        
    def yt_on_channel_closed(self,channel, reason):
        print("youtuber's channel is closing, and so is connection to youtuber-service,",reason)
        self.youtuber_con.close()

    def us_on_channel_closed(self,channel, reason):
        print("user's channel is closing, and so is connection to youtuber-service,",reason)
        self.youtuber_con.close()
    
    def nt_on_channel_closed(self,channel, reason):
        print("notification's channel is closing, and so is connection to youtuber-service,",reason)
        self.youtuber_con.close()
    
    def yt_on_queue_declareok(self,_):
        self.youtuber_ch.add_on_cancel_callback(self.yt_on_consumer_cancelled)
        self.youtuber_ch.basic_consume(
            "upload_video", self.consume_youtuber)
    
    def yt_on_consumer_cancelled(self,_):
        if self.youtuber_ch:
            self.youtuber_ch.close()

    def us_on_consumer_cancelled(self,_):
        if self.user_ch:
            self.user_ch.close()

try:  
    Server_P().start()
except KeyboardInterrupt:
    Server_P().stop()
