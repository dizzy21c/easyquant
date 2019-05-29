
# coding:utf-8
import sys
import traceback
import talib
import numpy as np
from pandas import Series

class StrategyTool:
  
  def __init__(self):
    self.init()

  def init(self):
    pass

  def cross(self, A, B):
    var = np.where(A < B, 1, 0)
    return (Series(var, index=A.index).diff() < 0).apply(int)


  def chk_dpfk(self, C=Series(), H=Series(), L=Series(), O=Series(), sd=6, ld=12):
    dsize = len(C)
    if dsize <= 12:
      return {}

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

    if self.cross(DLX, b5):
      buy50 = 1
    else:
      buy50 = 0
    
    if self.cross(DLX, b3):
      buy30 = 1
    else:
      buy30 = 0
    
    if self.cross(DLX, s5):
      sell5 = 1
    else:
      sell5 = 0
    
    if self.cross(DLX, s0):
      sell0 = 1
    else:
      sell0 = 0
    
    # j5:IF(CROSS(DLX,0.5),1.2,0.5);
    # j3:IF(CROSS(DLX,1.3),1.8,0.5);
    # s5:IF(CROSS(DLX,3.3),2.1,0.5);
    # sa:IF(CROSS(DLX,3.5),2.7,0.5);


    return {'b1':buy50, 'b2':buy30, 's1':sell5, 's0':sell0}

if __name__ == '__main__':
  c = StrategyTool()
  # O = []
  # C = []
  # H = []
  # L = []
  # c.chk_dpfk(C, H, L, O)