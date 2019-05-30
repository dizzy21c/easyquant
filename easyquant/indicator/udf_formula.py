
# coding:utf-8
import sys
import traceback
import talib
import numpy as np
import pandas as pd
from pandas import Series
from .base import *

class BaseFormula:

  name = "base-formula"

  def __init__(self):
    # self.H = data.high
    # self.L = data.low
    # self.O = data.open
    # self.C = data.close

    # self.V = data.volume
    # self.D = data.date
    self.init()

  def init(self):
    pass

  def cross(self, A, B):
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
      ls = len(A)
      A1 = A.iloc[ls -2]
      A0 = A.iloc[ls -1]
      B1 = B.iloc[ls -2]
      B0 = B.iloc[ls -1]
      
    if A1 < B1 and A0 > B0:
      return True

    return False

  # def cross(self, A, B):
  #   var = np.where(A < B, 1, 0)
  #   return (Series(var, index=A.index).diff() < 0).apply(int)

  def check(self, C=Series(), H=Series(), L=Series(), O=Series(), sd=6, ld=12):
    pass

class UdfIndexRisk(BaseFormula):
  name = "index-risk"

  def init(self):
    self.name = "index-risk"


  def check(self, C=Series(), H=Series(), L=Series(), O=Series(), sd=6, ld=12):
    dsize = len(C)
    if dsize <= 12:
      return {'flg':0}

    s0=3.5
    s5=3.3
    b3=1.3
    b5=0.5
    VAR2 = talib.MIN(L, sd)
    VAR3 = talib.MAX(H, ld)

    DLX=talib.EMA((C-VAR2)/(VAR3-VAR2)*4,4) #,COLORRED,LINETHICK1;
    # print(DLX[-10:])

    xz = dsize - 1
    zt = dsize - 2
    flg = 0
    if self.cross(DLX, b5):
      buy50 = 1
    else:
      buy50 = 0
    flg = flg + buy50

    if self.cross(DLX, b3):
      buy30 = 1
    else:
      buy30 = 0
    flg = flg + buy30

    if self.cross(DLX, s5):
      sell5 = 1
    else:
      sell5 = 0
    flg = flg + sell5
    
    if self.cross(DLX, s0):
      sell0 = 1
    else:
      sell0 = 0

    flg = flg + sell0
    
    return {'flg':flg, 'b1':buy50, 'b2':buy30, 's1':sell5, 's0':sell0}


class UdfMarketStart(BaseFormula):

  def check(self, C=Series(), H=Series(), L=Series(), O=Series(), sd=20, ld=250):
    A1 = (C-MA(C,ld))/MA(C,ld)*100
    N1 = BARSLAST(CROSS(C,MA(C,ld)), 1)
    N2 = BARSLAST(CROSS(MA(C,ld),C), 1)
    B1 = IF(N1<N2,N1+1,0)
    C1 = HHV(A1,B1)
    D1 = (C-REF(C,B1))/REF(C,B1)*100
    N3 = BARSLAST(CROSS(C,MA(C,sd)))
    N4 = BARSLAST(CROSS(MA(C,sd),C))
    AA = IF(N3<N4,N3+1,0)
    BB = (C-REF(C,AA))/REF(C,AA)*100 #,COLORRED
    if self.cross(BB, 10.0) and C/REF(C,1) > 1.05:
      return True
    else:
      return False
    # DRAWTEXT(CROSS(BB,10) AND C/REF(C,1)>1.05,8,'行情启动')


    # return super().check(C=C, H=H, L=L, O=O, sd=sd, ld=ld)

# if __name__ == '__main__':
#   c = StrategyTool()
#   # O = []
#   # C = []
#   # H = []
#   # L = []
#   # c.chk_dpfk(C, H, L, O)

