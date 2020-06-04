
from easyquant import EasyMq

a = EasyMq()

a.init_receive(exchange='stockcn')
a.add_sub_key('000735')
a.add_sub_key('000410')

a.start()
