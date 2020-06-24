import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
from easyquant.indicator import base
from easyquant.indicator.udf_formula import *

import pandas as pd
import random

import numpy as np

def CALC_FUN(data, SHORT=12, LONG=26, M=9):
    close=data.close
    mid=3*(data.close+data.low+data.high)/6
    qsx=(20*mid+19*base.REF(mid,1)) / 20
    data['BUY']=base.CROSS(data.close,qsx)
    data['SELL'] = base.CROSS(qsx, data.close)
    return data

# 公式名称: 口袋支点
def Koudai_Fun(data):
    def ff(x):
        if x['TJ21'] and x['TJ22'] and x['TJ23'] and x['TJ241'] and x['TJ242'] and x['TJ243']:
            return True
        #     if x.value == True:
        #         return True
        else:
            return False

    CLOSE = data.close
    OPEN = data.open
    VOL = data.vol
    df = pd.DataFrame()
    TJ1 = IF(OPEN > CLOSE, VOL, 0)
    df['TJ21'] = CLOSE / REF(CLOSE, 1) > 1.01
    df['TJ22'] = VOL > REF(HHV(TJ1, 10), 1)
    df['TJ23'] = CLOSE > OPEN
    df['TJ241'] = CLOSE > MA(CLOSE, 10)
    df['TJ242'] = CLOSE > MA(CLOSE, 50)
    df['TJ243'] = CLOSE > MA(CLOSE, 120)
    df['OUT'] = df.apply(lambda x: ff(x), axis=1)
    # df[df['out'] == True]
    return df
    #
    # CLOSE=data.close
    # OPEN=data.open
    # VOL=data.vol
    # TJ1 = IF(OPEN > CLOSE, VOL, 0)
    # TJ21 = CLOSE/REF(CLOSE,1)>1.01
    # TJ22 = VOL > REF(HHV(TJ1, 10),1)
    # TJ23 = CLOSE > OPEN
    # TJ241 = CLOSE > MA(CLOSE, 10)
    # TJ242 = CLOSE > MA(CLOSE, 50)
    # TJ243 = CLOSE > MA(CLOSE, 120)
    # TJ2 = TJ21 and TJ22
    # # TJ2 = CLOSE / REF(CLOSE, 1) > 1.01 AND  VOL > REF(HHV(TJ1, 10), 1)  AND  CLOSE > OPEN
    # # AND    CLOSE > MA10    AND    # CLOSE > MA50    AND    CLOSE > MA120;
    # # DRAWICON(BARSSINCEN(TJ2, 10) = 0, LOW * 0.98, 9);

def DingDi_fun(data):
    CLOSE=data.close
    LOW=data.low
    HIGH=data.high
    OPEN=data.open
    VOL=data.vol
    VAR1 = 1 / WINNER(CLOSE)
    VAR2 = MA(CLOSE, 13)
    VAR3 = 100 - ABS((CLOSE - VAR2) / VAR2 * 100)
    VAR4 = LLV(LOW, 75)
    VAR5 = HHV(HIGH, 75)
    VAR6 = (VAR5 - VAR4) / 100
    VAR7 = SMA((CLOSE - VAR4) / VAR6, 20, 1)
    VAR8 = SMA((OPEN - VAR4) / VAR6, 20, 1)
    VAR9 = 3 * VAR7 - 2 * SMA(VAR7, 15, 1)
    VARA = 3 * VAR8 - 2 * SMA(VAR8, 15, 1)
    VARB = 100 - VARA
    VARC = 1 #IF(900101 < 99991230, 1, 0)
    # 看（我）实力: (100 - VAR9) * VARC, , {000 B0001};
    KWSL = (100 - VAR9) * VARC
    散户区 = MA(WINNER(CLOSE * 0.95) * 100, 3) * VARC
    新庄区 = (100 - IF(VAR1 > 5, IF(VAR1 < 100, VAR1, VAR3 - 10), 0)) * VARC
    VARD = 散户区 > VAR3
    VARE = REF(LOW, 1) * 0.9
    VARF = LOW * 0.9
    VAR10 = (VARF * VOL + VARE * (CAPITAL - VOL)) / CAPITAL
    VAR11 = EMA(VAR10, 30)
    VAR12 = CLOSE - REF(CLOSE, 1)
    VAR13 = MAX(VAR12, 0)
    VAR14 = ABS(VAR12)
    # VAR15 = SMA(VAR13, 7, 1) / SMA(VAR14, 7, 1) * 100
    # VAR16 = SMA(VAR13, 13, 1) / SMA(VAR14, 13, 1) * 100
    VAR17 = BARSCOUNT(CLOSE)
    VAR18 = SMA(MAX(VAR12, 0), 6, 1) / SMA(ABS(VAR12), 6, 1) * 100
    VAR19 = (-200) * (HHV(HIGH, 60) - CLOSE) / (HHV(HIGH, 60) - LLV(LOW, 60)) + 100
    VAR1A = (CLOSE - LLV(LOW, 15)) / (HHV(HIGH, 15) - LLV(LOW, 15)) * 100
    VAR1B = SMA((SMA(VAR1A, 4, 1) - 50) * 2, 3, 1)
    VAR1C = (INDEXC - LLV(INDEXL, 14)) / (HHV(INDEXH, 14) - LLV(INDEXL, 14)) * 100;
    VAR1D = SMA(VAR1C, 4, 1)
    VAR1E = SMA(VAR1D, 3, 1)
    VAR1F = (HHV(HIGH, 30) - CLOSE) / CLOSE * 100
    '''
    VAR20 = VAR18 <= 25   
    AND    VAR19 < -95    AND    VAR1F > 20    
    AND    VAR1B < -30    AND    VAR1E < 30    
    AND    VAR11 - CLOSE >= -0.25
    AND    VAR15 < 22    AND    
    VAR16 < 28    AND    VAR17 > 50
    '''
    VAR21 = (HIGH + LOW + CLOSE) / 3
    VAR22 = (VAR21 - MA(VAR21, 14)) / (0.015 * AVEDEV(VAR21, 14))
    VAR23 = (VAR21 - MA(VAR21, 70)) / (0.015 * AVEDEV(VAR21, 70))
    VAR24 = IF(VAR22 >= 150 and    VAR22 < 200    and    VAR23 >= 150 AND    VAR23 < 200, 10, 0)
    VAR25 = IF(VAR22 <= -150    and    VAR22 > -200 and    VAR23 <= -150    and    VAR23 > -200, -10, VAR24)
    VAR26 = (CLOSE - LLV(LOW, 27)) / (HHV(HIGH, 27) - LLV(LOW, 27)) * 100
    VAR27 = REVERSE(VAR26)
    VAR28 = SMA(VAR26, 3, 1)
    散户 = SMA(VAR28, 3, 1) * VARC
    新庄 = SMA(散户, 3, 1) * VARC
    地狱 = IFAND(CROSS(散户, 新庄)    ,    散户 < 30, 新庄, 0)*VARC
    天堂 = IFAND(CROSS(新庄, 散户)    ,    新庄 > 75, 新庄, 100)*VARC
    # DRAWTEXT(CROSS(散户, 新庄)    AND    散户 < 30, 新庄, '逢低吸呐 ！')
    # DRAWTEXT(CROSS(新庄, 散户)    AND    新庄 > 75, 新庄, '逢高减磅！')
    小心断裂: (IF(VAR23 >= 200 and VAR22 >= 150, 15, IF(VAR23 <= -200 and VAR22 <= -150, -15, VAR25))+50)*VARC #,, {00050006};
    # DRAWTEXT(CROSS(VAR20, 0.5)    AND    COUNT(VAR20=1, 10) = 1, 35, '抄底'), , COLORYELLOW;
    抄底 = CROSS(VAR20, 0.5)    and    COUNT(VAR20=1, 10) = 1
    # DRAWTEXT(CROSS(VARD, 0.5)    AND    COUNT(VARD=1, 10) = 1, 65, '逃顶'), , ;
    # STICKLINE(VARD, 100, 25, 1, 0),, ;
    # STICKLINE(1, 散户区, 0, 1, 0),, COLORYELLOW;
    逃顶 = CROSS(VARD, 0.5)   and COUNT(VARD=1, 10) = 1
    # STICKLINE(1, 新庄区, 100, 1, 0),, {00010001};
    # STICKLINE(VAR20, 0, 80, 1, 0),, COLORRED;

