# utf-8
from easyquant import RedisIo
from easyquant.indicator.base import *
from ctypes import * # cdll, c_int
import numpy as np
import pandas as pd
lib  = cdll.LoadLibrary('./easyquant/czsc_cpp/czsc.so')
r=RedisIo('redis.conf')

# addBuf = lib.addBuf
# func2=lib.Func2

a1=r.get_day_df('000001', startpos=1000)

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


# for i in range(0,ncount):
#   print("f1=%d hib=%6.2f lob=%6.2f sig=%6.2f bsp=%6.2f slp=%6.2f" % \
#     (DLL[i], HIB[i], LOB[i], SIG[i],BSP[i],SLP[i]))


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

def klineplot(data_df,dll,*avg_line):
    # from IPython.core.display import display, HTML
    from pyecharts import Kline
    from pyecharts import Line
    from pyecharts import Bar
    from pyecharts import Overlap
    from pyecharts import Grid
    # import warnings
    import pandas as pd
    # for i in range(len(data_df)):
    #     if data_df["vol"][i] < 0:
    #         data_df["vol"][i]=0

    if ("time" in data_df) and ("date" in data_df):
        date=data_df["date"]+" "+data_df["time"]
    if "time" not in data_df.columns:
        date=data_df["date"]
    if "date" not in data_df.columns:
        date=data_df["time"]
    x=[]
    for i in range(len(data_df)):
        y=[data_df["open"][i],data_df["close"][i],data_df["low"][i],data_df["high"][i]]
        x.append(y)
    kline = Kline()
    kline.add("high",date,x,
            tooltip_tragger="axis",is_datazoom_show=True,tooltip_axispointer_type='cross',
            is_legend_show=False,is_more_utils=True,yaxis_min=(min(data_df["low"])-(max(data_df["high"])-min(data_df["low"]))/4))

    line2=Line()
    p_list=["open","close","low"]
    for i in p_list:
        line2.add(i,date,data_df[i],tooltip_tragger="axis",line_opacity=0)

    # for cd in dll:
    #   if cd > 0:
    #     data_df[]
    line_c = Line()
    # ld=len(dll)
    # for i in range(0, ld):#dll:
    dll2=dll[dll==0]
    data_df['dll'] = dll
    line_c.add("dll",date, data_df['dll'],tooltip_tragger="axis")
      # print(d)
    ma_list=avg_line
    # print(ma_list)
    if len(ma_list)>0:
        line1=Line()
        i = 0
        for ma in ma_list:
            print(ma)
            # data_df['MA_' + str(ma)] = pd.Series.rolling(data_df['close'], ma).mean()
            data_df['MA_%d' % i] = ma
            line1.add("MA_%d"%i, date,data_df['MA_%d'%i],tooltip_tragger="axis")

    bar = Bar()
    bar.add("vol", date, data_df["vol"],tooltip_tragger="axis",is_legend_show=False,is_yaxis_show=False,yaxis_max=5*max(data_df["vol"]))

    overlap = Overlap() #width="80%", height=800)
    overlap.add(kline)
    overlap.add(line_c)
    # overlap.add(line2)
    if len(ma_list)>0:
        overlap.add(line1)
    # overlap.add(bar,yaxis_index=1, is_add_yaxis=True)

    # grid = Grid()
    grid = Grid(width=1360, height=700, page_title='QUANTAXIS')
    # grid.add(overlap, grid_top="30%")
    grid.add(bar, grid_top="50%")
    grid.add(overlap, grid_bottom="20%")


    # overlap.render("test.html")
    grid.render("test.html")
    # display(HTML(overlap._repr_html_()))
    # warnings.filterwarnings("ignore")


# for i in range(0,ncount):
#   print("f1=%d hib=%6.2f lob=%6.2f sig=%6.2f bsp=%6.2f slp=%6.2f" % \
#     (DLL[i], HIB[i], LOB[i], SIG[i],BSP[i],SLP[i]))
DLL=pd.Series(np.asarray(DLL))
HIGH=a1.high
LOW=a1.low
DLL=IF(DLL>0,HIGH,IF(DLL<0,LOW,0))
# klineplot(a1, DLL, HIB, LOB, SIG)
klineplot(a1, DLL)