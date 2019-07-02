# utf-8
from easyquant import RedisIo
from ctypes import * # cdll, c_int
import numpy as np
lib  = cdll.LoadLibrary('./easyquant/chanlunx_cpp/chanlunx.so')
r=RedisIo('redis.conf')

# addBuf = lib.addBuf
# func2=lib.Func2

a1=r.get_day_df('000001')

ncount=len(a1)
tf_p=c_float * ncount
FRAC1 = tf_p(0)
FRAC2 = tf_p(0)
DUAN1 = tf_p(0)
DUAN2 = tf_p(0)
DUANZG1 = tf_p(0)
DUANZD1 = tf_p(0)
DUANSE1 = tf_p(0)
DUANZG2 = tf_p(0)
DUANZD2 = tf_p(0)
DUANSE2 = tf_p(0)

vig=0 #tf_p(0)

nh=np.asarray(a1['high']).astype(np.float32)
nl=np.asarray(a1['low']).astype(np.float32)

H=cast(nh.ctypes.data, POINTER(c_float))
L=cast(nl.ctypes.data, POINTER(c_float))

lib.Func1(ncount, FRAC1, H, L, vig)
lib.Func2(ncount, FRAC2, H, L, vig)

lib.Func3(ncount, DUAN1, FRAC2, H, L)
lib.Func5(ncount, DUANZG1, DUAN1, H, L)
lib.Func6(ncount, DUANZD1, DUAN1, H, L)
lib.Func7(ncount, DUANSE1, DUAN1, H, L)

lib.Func3(ncount, DUAN2, FRAC1, H, L)
lib.Func5(ncount, DUANZG2, DUAN2, H, L)
lib.Func6(ncount, DUANZD2, DUAN2, H, L)
lib.Func7(ncount, DUANSE2, DUAN2, H, L)

# for i in range(0,ncount):
#   print("f1=%d f2=%d d1=%d d2=%d zg1=%6.2f zd1=%6.2f se1=%6.2f zg2=%6.2f zd2=%6.2f se2=%6.2f" % \
#     (FRAC1[i], FRAC2[i], DUAN1[i], DUAN2[i],DUANZG1[i],DUANZD1[i],DUANSE1[i],DUANZG2[i],DUANZD2[i],DUANSE2[i]))
