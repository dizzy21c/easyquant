
# coding:utf-8
import sys
import traceback
import talib
import numpy as np
import pandas as pd
from pandas import Series
from .base import *

def udf_cross(A, B):
  if isinstance(A, float):
    A1 = A0 = A
    ls = len(B)
    B1 = B.iloc[ls -2]
    B0 = B.iloc[ls -1]
  elif isinstance(B, float):
    B1 = B0 = B
    ls = len(A)
    A1 = A.iloc[ls -2]
    A0 = A.iloc[ls -1]
  else:
    return SINGLE_CROSS(A,B)
    
  if A1 < B1 and A0 > B0:
    return True
  return False

def udf_ref_pct(A, B, N = 1):
  if len(A) < N + 1:
    return False
  C = A / REF(A, N)
  lc = len(C)
  return C[lc - 1] > B

def udf_dapan_risk_df(data_df, N1=6, N2=12):
  dsize = len(data_df)
  if dsize <= N2:
    return (False, None)

  return udf_dapan_risk(data_df.close, data_df.high, data_df.low, N1, N2) 

def udf_dapan_risk(C,H,L, N1=6, N2=12):
  dsize = len(C)
  if dsize <= N2:
    return (False, None)

  # C = data_df.close
  # H = data_df.high
  # L = data_df.low

  s0=3.5
  s5=3.3
  b3=1.3
  b5=0.5
  # VAR2 = talib.MIN(L, N1)
  # VAR3 = talib.MAX(H, N2)
  VAR2 = LLV(L, N1)
  VAR3 = HHV(H, N2)

  DLX=talib.EMA((C-VAR2)/(VAR3-VAR2)*4,4)

  flg = 0
  if udf_cross(DLX, b5):
    buy50 = 1
  else:
    buy50 = 0
  flg = flg + buy50

  if udf_cross(DLX, b3):
    buy30 = 1
  else:
    buy30 = 0
  flg = flg + buy30

  if udf_cross(DLX, s5):
    sell5 = 1
  else:
    sell5 = 0
  flg = flg + sell5
  
  if udf_cross(DLX, s0):
    sell0 = 1
  else:
    sell0 = 0

  flg = flg + sell0
  
  return (flg > 0, {'buy50':buy50, 'buy30':buy30, 'sell5':sell5, 'sella':sell0})

def udf_base_check_df(data_df, N1=70, N2=144, N3=250):
  return udf_base_check(data_df.close, data_df.vol, N1, N2, N3)

def udf_base_check(C, V, N1=70, N2=144, N3=250):
  len_d = len(C)
  N = MAX(MAX(N1,N2),N3)
  if len_d < N:
    return (False, None)

  len_d -= 1
  # C = data_df.close
  # V = data_df.vol
  
  cn1 = C > MA(C, N1)
  cn2 = C > MA(C, N2)
  cn3 = C > MA(C, N3)
  
  return (cn1[len_d] or cn2[len_d] or cn3[len_d], {str(N1):cn1[len_d], str(N2):cn2[len_d], str(N3):cn3[len_d]})

def udf_hangqing_start_df(data_df, snum=13, lnum=144):#, sd=20, ld=250):
  return udf_hangqing_start(data_df.close, sum, lnum)

def udf_hangqing_start(C, snum=13, lnum=144):#, sd=20, ld=250):
  if len(C) < lnum:
    return False

  # C = data_df.close

  A1 = (C-MA(C,lnum))/MA(C,lnum)*100
  N1 = BARSLAST(CROSS(C,MA(C,lnum)), 1)
  N2 = BARSLAST(CROSS(MA(C,lnum),C), 1)
  B1 = IF(N1<N2,N1+1,0)
  C1 = HHV(A1,B1)
  D1 = (C-REF(C,B1))/REF(C,B1)*100
  N3 = BARSLAST(CROSS(C,MA(C,snum)))
  N4 = BARSLAST(CROSS(MA(C,snum),C))
  AA = IF(N3<N4,N3+1,0)
  BB = (C-REF(C,AA))/REF(C,AA)*100

  # IFAND(udf_cross(BB, 10.0), C/REF(C,1) > 1.05, True, False)
  return udf_cross(BB, 10.0) and udf_ref_pct(C, 1.05)

def udf_niu_check_df(data_df, n1 = 36, n2 = 30, n3 = 25):
  return udf_niu_check(data_df.close, data_df.high, data_df.low, data_df.vol, data_df.amount, n1, n2, n3)

def udf_niu_check(CLOSE,HIGH,LOW,VOL,AMOUNT, n1 = 36, n2 = 30, n3 = 25):
  if len(CLOSE) > n1:
    return False

  # LOW = data_df.low
  # HIGH = data_df.high
  # CLOSE=data_df.close
  # VOL=data_df.volume
  VARR24=LLV(LOW,36)
  VARR25=HHV(HIGH,30)
  VARR26=EMA((CLOSE-VARR24)/(VARR25-VARR24)*4,4)*25
  VARB27=(((CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100)/2+22)*1
  VARB28=(((CLOSE -(((EMA(AMOUNT*100,13) /EMA(VOL,13)) / 100))) / (((EMA(AMOUNT*100,13) /EMA(VOL,13)) / 100))) * 100)
  # JD=((VARB28 < (0)) AND ((CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100)<VARB27-2 AND VARR26<10
  JD1 = (VARB28 < (0))
  JD2 = ((CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100)<VARB27-2
  JD3 = VARR26<10
  JD4=IFAND(JD1,JD2,JD1,False)
  JD=IFAND(JD4,JD3,JD4,False)
  CD=IF(JD,20,0)
  AAA=REF(CD,1)>0
  # BBB=CD=0
  # DR=AAA AND BBB
  # return JD OR DR
  RTN=IFOR(JD, AAA, True, False)
  lrtn = len(RTN)
  return RTN[lrtn - 1] or RTN[lrtn - 2] or RTN[lrtn - 3]

  
def udf_top_df(data_df):
  return udf_top(data_df.close, data_df.high, data_df.low)

def udf_top(C,H,L):
  # {涨停板次日跳空高开的选股}
  # REF(C,1)/REF(C,2)>1.098 AND REF(C,1)=REF(H,1) AND L>REF(H,1);
  len_d = len(C)
  if len_d < 2:
    return False
  
  # C=data_df.close
  # H=data_df.high
  # L=data_df.low
  
  A1=REF(C,1)/REF(C,2)>1.098
  A2=REF(C,1)==REF(H,1)
  A3=L>REF(H,1)
  
  A4 = IFAND(IFAND(A1,A2,True,False),A3,True,False)
  return A4[len_d - 1]
  
  
def udf_top_last(C, PCT = 9.8, M = 5, N=30):
  len_d = len(C) - 1
  if len_d < N:
    return False

  rtn = False
  if M <= 0:
    M = 5
  for i in range(0, M):
    A = (REF(C,i) - REF(C,i+1)) * 100 /REF(C,i+1) > PCT
    if A[len(A)-1]:
      rtn = True
      break
    
  return rtn