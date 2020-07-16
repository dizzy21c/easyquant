#!/usr/bin/env python

# from QAPUBSUB import producer
#
import gpzs_order_pb2
from easymq import EasyMq

def test_pub():
    easymq = EasyMq(host='192.168.3.8')
    easymq.init_pub(exchange="zsorder2")

    # easymq.pub(json.dumps(stdata), stcode)


    zsorder = gpzs_order_pb2.gpzs_order()
    zsorder.code = '000001'
    zsorder.vol = 1000
    zsorder.price = 0.0
    zsorder.bsflg = 1
    zsorder.zsno = 0

    # p.pub('xxxxx',routing_key='x1')

    # p.pub('1',routing_key='x2')
    print(zsorder.SerializeToString())

    # p.pub(zsorder.SerializeToString())
    easymq.pub(zsorder.SerializeToString(), '000001')

# def test_sub():
#     easymq = EasyMq()
#     easymq.init_pub(exchange="zsorder")

if __name__ == "__main__":
    test_pub()

