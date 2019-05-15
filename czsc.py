# utf-8
from easyquant import RedisIo
from ctypes import * # cdll, c_int
import numpy as np
lib  = cdll.LoadLibrary('./easyquant/czsc_cpp/czsc.so')
r=RedisIo('redis.conf')

# addBuf = lib.addBuf
# func2=lib.Func2

a1=r.get_day_df('000001')

ncount=len(a1)
tf_p=c_float * ncount
DLL = tf_p(0)
HIB = tf_p(0)
LOB = tf_p(0)
SIG = tf_p(0)
BSP = tf_p(0)
SLP = tf_p(0)

vig=5

nh=np.asarray(a1['high']).astype(np.float32)
nl=np.asarray(a1['low']).astype(np.float32)

H=cast(nh.ctypes.data, POINTER(c_float))
L=cast(nl.ctypes.data, POINTER(c_float))

lib.Func1(ncount, DLL, H, L, vig)
lib.Func2(ncount, HIB, DLL, H, L)
lib.Func3(ncount, LOB, DLL, H, L)
lib.Func4(ncount, SIG, DLL, H, L)
lib.Func5(ncount, BSP, DLL, H, L)
lib.Func8(ncount, SLP, DLL, H, L)


for i in range(0,ncount):
  print("f1=%d hib=%6.2f lob=%6.2f sig=%6.2f bsp=%6.2f slp=%6.2f" % \
    (DLL[i], HIB[i], LOB[i], SIG[i],BSP[i],SLP[i]))


# DLL:=TDXDLL1(1,H,L,5);
# HIB:=TDXDLL1(2,DLL,H,L);
# LOB:=TDXDLL1(3,DLL,H,L);
# SIG:=TDXDLL1(4,DLL,H,L);
# BSP:=TDXDLL1(5,DLL,H,L);
# SLP:=TDXDLL1(8,DLL,H,L);
# BUY(BSP=3,LOW);
# SELL(BSP=12,HIGH);
# BUYSHORT(BSP=2,LOW);
# SELLSHORT(BSP=13,HIGH);