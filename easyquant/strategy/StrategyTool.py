
# coding:utf-8
import sys
import traceback
import talib
import numpy as np

class StrategyTool:
  
  def __init__(self):
    pass

  def chk_dpfk_01(self, C=close,H=high,L=low,O=open):
    # pass
    w1=3.5
    w2=3.3
    w3-1.3
    w4=0.5
    VAR2 = talib.MIN(L, 6)
    # VAR2:=LLV(LOW,6);
    # VAR3:=HHV(HIGH,12);  
    VAR3 = talib.MAX(H, 12)

    DLX=talib.EMA((C-VAR2)/(VAR3-VAR2)*4,4),COLORRED,LINETHICK1;
    # print(DLX[-5:])
    # 进五成:IF(CROSS(DLX,0.5),1.2,0.5);
    # 加三成:IF(CROSS(DLX,1.3),1.8,0.5);
    # 减半:IF(CROSS(DLX,3.3),2.1,0.5);
    # 清仓:IF(CROSS(DLX,3.5),2.7,0.5);


    # STICKLINE(C,1.3,1.3,2,0),COLOR777777;
    # STICKLINE(C,3.3,3.3,2,0),COLOR777777;
    # STICKLINE(C,3.5,3.5,2,0),COLORAAAA55;

if __name__ == '__main__':
  c = StrategyTool
  O = []
  C = []
  H = []
  L = []
  c.chk01(O,C,H,L)