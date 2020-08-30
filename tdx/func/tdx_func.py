
import pandas as pd
from easyquant.indicator.base import *

def new_df(df_day, data, now_price):
    code = data['code']
    # now_vol = data['volume']
    last_time = pd.to_datetime(data['datetime'][0:10])
    # print("code=%s, data=%s" % (self.code, self._data['datetime']))
    # df_day = data_buf_day[code]
    # df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
    df_day.loc[(last_time, code), 'open'] = data['open']
    df_day.loc[(last_time, code), 'high'] = data['high']
    df_day.loc[(last_time, code), 'low'] = data['low']
    df_day.loc[(last_time, code), 'close'] = now_price
    df_day.loc[(last_time, code), 'vol'] = data['volume']
    df_day.loc[(last_time, code), 'amount'] = data['amount']
    return df_day

def tdx_hm(data):
    # A1 := ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23));
    # A2 := DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1);
    # 金线王 := EMA(A2, 200) * 1.118;
    # 条件 := (C - REF(C, 1)) / REF(C, 1) * 100 > 8;
    # 金K线: CROSS(C, 金线王) AND 条件;
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    C = data.close
    H = data.high
    O = data.open

    A1 = ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23))
    A2 = DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1)
    金线王 = EMA(A2, 200) * 1.118
    条件 = (C - REF(C, 1)) / REF(C, 1) * 100 > 8
    金K线 = IFAND(CROSS(C, 金线王), 条件, True, False)
    return 金K线, False
# 大黑马出笼
def tdx_dhmcl(data):
    CLOSE = data.close
    OPEN = data.open
    C = data.close
    H = data.high
    O = data.open
    # TDX-FUNC
    # QQ := ABS(MA(C, 10) / MA(C, 20) - 1) < 0.01;
    # DD := ABS(MA(C, 5) / MA(C, 10) - 1) < 0.01;
    # QD := ABS(MA(C, 5) / MA(C, 20) - 1) < 0.01;
    # DQ := MA(C, 5) > REF(MA(C, 5), 1) and QQ and DD and QD;
    # QQ1 := (MA(C, 3) + MA(C, 6) + MA(C, 12) + MA(C, 24)) / 4;
    # QQ2 := QQ1 + 6 * STD(QQ1, 11);
    # QQ3 := QQ1 - 6 * STD(QQ1, 11);
    # DD1 := MAX(MAX(MA(C, 5), MA(C, 10)), MAX(MA(C, 10), MA(C, 20)));
    # DD2 := MIN(MIN(MA(C, 5), MA(C, 10)), MIN(MA(C, 10), MA(C, 20)));
    # B: EVERY(OPEN > CLOSE, 3);
    # B9 := "MACD.MACD" > 0;
    # B1 := C / REF(C, 1) > 1.03;
    # ZZ: O <= DD2 and C >= DD1 and REF(C < O, 1) and C > QQ2 and C > QQ1 and QQ1 > O and O / QQ3 < 1.005 and DQ;
    # B2 := SMA(MAX(CLOSE - REF(C, 1), 0), 2, 1) * C * 102;
    # B3 := SMA(ABS(CLOSE - REF(C, 1)), 2, 1) * C * 100;
    # B4 := B2 / B3 * 100 < 10;
    # B5 := B and B4;
    # B6 := MA(C, 5) < REF(MA(C, 5), 1);
    # B7 := REF(MA(C, 5), 4) > REF(MA(C, 5), 5);
    # B8 := (H - C) / C * 100 < 1 and REF((O - C) / C * 100 > 1, 1) and KDJ.J > 25;
    # 大黑马出笼: C > O and B1 and B6 and B7 and B8 and REF(B5, 1) and B9 or ZZ;
    # python
    QQ = ABS(MA(C, 10) / MA(C, 20) - 1) < 0.01
    DD = ABS(MA(C, 5) / MA(C, 10) - 1) < 0.01
    QD = ABS(MA(C, 5) / MA(C, 20) - 1) < 0.01
    DQ = IFAND4(MA(C, 5) > REF(MA(C, 5), 1), QQ, DD, QD, True, False)
    QQ1 = (MA(C, 3) + MA(C, 6) + MA(C, 12) + MA(C, 24)) / 4
    QQ2 = QQ1 + 6 * STD(QQ1, 11)
    QQ3 = QQ1 - 6 * STD(QQ1, 11)
    DD1 = MAX(MAX(MA(C, 5), MA(C, 10)), MAX(MA(C, 10), MA(C, 20)))
    DD2 = MIN(MIN(MA(C, 5), MA(C, 10)), MIN(MA(C, 10), MA(C, 20)))
    # BT1=IFAND3(REF(OPEN,1)>REF(CLOSE,1),REF(OPEN,2)>REF(CLOSE,2),True,False)
    # B = EVERY(OPEN > CLOSE, 3)
    B = IFAND3(O > C, REF(OPEN, 1) > REF(CLOSE, 1), REF(OPEN, 2) > REF(CLOSE, 2), True, False)
    # B9=MACD(C,12,26,9)
    B9 = MACD(C).MACD > 0
    B1 = C / REF(C, 1) > 1.03
    # ZZ = O <= DD2 and C >= DD1 and REF(C < O, 1) and C > QQ2 and C > QQ1 and QQ1 > O and O / QQ3 < 1.005 and DQ
    ZZ1 = IFAND6(O <= DD2, C >= DD1, REF(IF(C < O, 1, 0), 1) > 0, C > QQ2, C > QQ1, QQ1 > O, True, False)
    ZZ = IFAND3(ZZ1, O / QQ3 < 1.005, DQ, True, False)
    B2 = SMA(MAX(CLOSE - REF(C, 1), 0), 2, 1) * C * 102
    B3 = SMA(ABS(CLOSE - REF(C, 1)), 2, 1) * C * 100
    B4 = B2 / B3 * 100 < 10
    # B5 = B and B4
    B5 = IFAND(B, B4, True, False)
    B6 = MA(C, 5) < REF(MA(C, 5), 1)
    B7 = REF(MA(C, 5), 4) > REF(MA(C, 5), 5)
    # B8 = (H - C) / C * 100 < 1 and REF((O - C) / C * 100 > 1, 1) and KDJ.J > 25
    B81 = IFAND((H - C) / C * 100 < 1, REF(IF((O - C) / C * 100 > 1, 1, 0), 1), True, False)
    B8 = IFAND(B81, KDJ(data).KDJ_J > 25, True, False)
    HMTJ1 = IFAND5(C > O, B1, B6, B7, B8, True, False)
    HMTJ2 = IFAND3(HMTJ1, REF(IF(B5, 1, 0), 1) > 0, B9, True, False)
    # 大黑马出笼= C > O and B1 and B6 and B7 and B8 and REF(B5, 1) and B9 OR ZZ
    大黑马出笼 = IFOR(HMTJ2, ZZ, True, False)
    return 大黑马出笼, False

def tdx_sxp(data):
    CLOSE=data.close
    C=data.close
    前炮 = CLOSE > REF(CLOSE, 1) * 1.099
    小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 9
    小阴小阳1 = ABS(C - REF(C, 1)) / REF(C, 1) * 100 < 9
    时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, 1, 0)
    return 后炮, True

# 黑马大肉
def tdx_hmdr(data):
    # C1 := C / REF(C, 1);
    # MX := EMA(SLOPE(C, N2) * 20 + C, N1), LINETHICK1, COLORWHITE;
    # MXR := MX / REF(MX, 1);
    # MR := SLOPE(MX, 2);
    # MRD := CROSS(0, MR);
    # TMR := BARSLAST(MRD);
    # MRR := REF(MX, TMR);
    # MN3 := HHV(MRR, N3);
    # 有肉肉 := CROSS(MX, MRR) and MX / LLV(MX, 55) < 1.35;
    # 大肉1 := CROSS(C, MN3) and C1 > 1.035);
    # 大肉 := CROSS(C, MN3) and C1 > 1.035) and MXR > 1.004;
    #
    # {黑马}
    #
    # A1 := ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23));
    # A2 := DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1);
    # 金线王 := EMA(A2, 200) * 1.118;
    # 条件 := (C - REF(C, 1)) / REF(C, 1) * 100 > 8;
    # 金K线: CROSS(C, 金线王) and 条件 and 大肉;

    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    C = data.close
    H = data.high
    O = data.open
    N1 = 42
    N2 = 21
    N3 = 89

    C1 = C / REF(C, 1)
    MX = EMA(SLOPE(C, N2) * 20 + C, N1)
    MXR = MX / REF(MX, 1)
    MR = SLOPE(MX, 2)
    MRD = CROSS(0, MR)
    TMR = BARSLAST(MRD)
    MRR = REF(MX, TMR)
    MN3 = HHV(MRR, N3)
    有肉肉 = IFAND(CROSS(MX, MRR) , MX / LLV(MX, 55) < 1.35, True, False);
    # 大肉1 := CROSS(C, MN3) and C1 > 1.035);
    大肉 = IFAND(CROSS(C, MN3), C1 > 1.035, True, False)

    A1 = ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23))
    A2 = DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1)
    金线王 = EMA(A2, 200) * 1.118
    条件 = (C - REF(C, 1)) / REF(C, 1) * 100 > 8
    金K线 = IFAND3(CROSS(C, 金线王), 条件, 有肉肉, True, False)
    # return 金K线, False
    return 大肉, False
