
import gpzs_order_pb2
from easymq import EasyMq

odata = gpzs_order_pb2.gpzs_order()
def ucallback(a,b,c,data):

    # print(a)
    # print(b)
    # print(data)
    # print(type(data))
    # print(data)
    try:
        odata.ParseFromString(data)
        # odata.ParseFromBytes(data)
        # print("ok")
        print("v=%s, type=%s" % (odata.code, type(odata.code)))
        print("v=%s, type=%s" % (odata.vol, type(odata.vol)))
        print("v=%s, type=%s" % (odata.price, type(odata.price)))
        print("v=%s, type=%s" % (odata.bsflg, type(odata.bsflg)))
        print("v=%s, type=%s" % (odata.zsno, type(odata.zsno)))
    except Exception as e:
        print("error")
        print(e)

easymq = EasyMq(host='192.168.3.8')
easymq.init_receive(exchange="zsorder2")
easymq.callback = ucallback

# easymq.callback = lambda a,b,c,data: print(data)
# easymq.add_sub_key(routing_key='000001')
# easymq.callback = ucallback
# c = consumer.subscriber(exchange='zsorder')
# c.callback = ucallback
easymq.start()
