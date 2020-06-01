
import pika
import json

class EasyMq(object):
  # def __init__(self, , host=host, port=port, user=user, password=password, channel_number=1, queue_name='', routing_key='default',  exchange='', exchange_type='fanout', vhost='/'):
  def __init__(self, host='127.0.0.1', port=5672, user='admin', password='admin', channel_number=1, vhost='/'):
    self.host = host
    self.port = port
    self.user = user
    self.password = password

    # self.queue_name = queue_name
    # self.exchange = exchange
    # self.routing_key = routing_key
    self.vhost = vhost
    # self.exchange_type = exchange_type
    self.channel_number = channel_number
    # fixed: login with other user, pass failure @zhongjy
    credentials = pika.PlainCredentials(
        self.user, self.password, erase_on_connect=True)
    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost,
                                  credentials=credentials, heartbeat=0, socket_timeout=5,
                                  )
    )

    self.channel = self.connection.channel(
        channel_number=self.channel_number)

  def reconnect(self):
    try:
        self.connection.close()
    except:
        pass

    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.host, port=self.port,
                                  heartbeat=0, virtual_host=self.vhost,
                                  socket_timeout=5,))

    self.channel = self.connection.channel(
        channel_number=self.channel_number)
    return self
    
  
  def init_pub(self, exchange, queue_name = '', exchange_type='direct'):
    self.exchange = exchange
    self.queue_name = queue_name
    # self.routing_key = routing_key
    self.channel.queue_declare(
        self.queue_name, auto_delete=True, exclusive=True)
    self.channel.exchange_declare(exchange=exchange,
                                  exchange_type=exchange_type,
                                  passive=False,
                                  durable=False,
                                  auto_delete=False)
    
  
  def pub(self, text, routing_key):
    # channel.basic_publish向队列中发送信息
    # exchange -- 它使我们能够确切地指定消息应该到哪个队列去。
    # routing_key 指定向哪个队列中发送消息
    # body是要插入的内容, 字符串格式
    if isinstance(text, bytes):
      content_type = 'text/plain'
    elif isinstance(text, str):
      content_type = 'text/plain'
    elif isinstance(text, dict):
      content_type = 'application/json'
    try:
      self.channel.basic_publish(exchange=self.exchange,
        routing_key=routing_key,
        body=text,
        properties=pika.BasicProperties(content_type=content_type,
                                        delivery_mode=1))
    except Exception as e:
        print(e)
        self.reconnect().channel.basic_publish(exchange=self.exchange,
                routing_key=routing_key,
                body=text,
                properties=pika.BasicProperties(content_type=content_type,
                                                delivery_mode=1))

  def exit(self):
      self.connection.close()