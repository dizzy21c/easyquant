import pandas as pd
import os
import datetime
import numpy as np 
import statsmodels.formula.api as sml

import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.mlab as mlab
from easyquant.indicator.base import *

import json
from easyquant import MongoIo
import statsmodels.api as sm
from multiprocessing import Process, Pool, cpu_count, Manager

mongo = MongoIo()

data_buf1 = Manager().dict()
data_buf2 = Manager().dict()
pool_size = cpu_count()
print("pool size=%d" % pool_size)
def tdx_base_func(data, code_list = None):
    """
    准备数据
    """
    # highs = data.high
    # start_t = datetime.datetime.now()
    # print("begin-tdx_base_func:", start_t)

    CLOSE=data.close
    C=data.close
    前炮 = CLOSE > REF(CLOSE, 1) * 1.099
    小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 9
    时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, 1, 0)
    # return pd.DataFrame({'FLG': 后炮}).iloc[-1]['FLG']
    # return 后炮.iloc[-1]

    # 斜率
    data = data.copy()
    # data['bflg'] = IF(REF(后炮,1) > 0, 1, 0)
    data['bflg'] = 后炮
    # print("code=%s, bflg=%s" % (code, data['bflg'].iloc[-1]))
    # data['beta'] = 0
    # data['R2'] = 0
    # beta_rsquared = np.zeros((len(data), 2),)
    #
    # for i in range(N - 1, len(highs) - 1):
    # #for i in range(len(highs))[N:]:
    #     df_ne = data.iloc[i - N + 1:i + 1, :]
    #     model = sml.ols(formula='high~low', data = df_ne)
    #     result = model.fit()
    #
    #     # beta = low
    #     beta_rsquared[i + 1, 0] = result.params[1]
    #     beta_rsquared[i + 1, 1] = result.rsquared
    #
    # data[['beta', 'R2']] = beta_rsquared

    # 日收益率
    data['ret'] = data.close.pct_change(1)

    # 标准分
    # data['beta_norm'] = (data['beta'] - data.beta.rolling(M).mean().shift(1)) / data.beta.rolling(M).std().shift(1)
    #
    # beta_norm = data.columns.get_loc('beta_norm')
    # beta = data.columns.get_loc('beta')
    # for i in range(min(M, len(highs))):
    #     data.iat[i, beta_norm] = (data.iat[i, beta] - data.iloc[:i - 1, beta].mean()) / data.iloc[:i - 1, beta].std() if (data.iloc[:i - 1, beta].std() != 0) else np.nan

    # data.iat[2, beta_norm] = 0
    # data['RSRS_R2'] = data.beta_norm * data.R2
    # data = data.fillna(0)
    #
    # # 右偏标准分
    # data['beta_right'] = data.RSRS_R2 * data.beta
    # if code == '000732':
    #     print(data.tail(22))

    return data

def tdx_func(datam, code_list = None):
    """
    准备数据
    """
    # highs = data.high
    start_t = datetime.datetime.now()
    print("begin-tdx_func:", start_t)
    dataR = pd.DataFrame()
    if code_list is None:
        code_list = datam.index.levels[1]
    for code in code_list:
        data=datam.query("code=='%s'" % code)
        data = tdx_base_func(data)
        if len(dataR) == 0:
            dataR = data
        else:
            dataR = dataR.append(data)
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func spent:{}'.format((end_t - start_t)))
    return dataR.sort_index()

def tdx_func_mp(datam, code_list = None):
    pool = Pool(cpu_count())


def pre_rsrs_data_v2_func(data, N=18, M=252):
    """
    准备数据
    """
    highs = data.high

    # 斜率
    data['beta'] = 0
    data['R2'] = 0
    beta_rsquared = np.zeros((len(data), 2),)

    for i in range(N - 1, len(highs) - 1):
    #for i in range(len(highs))[N:]:
        df_ne = data.iloc[i - N + 1:i + 1, :]
        model = sml.ols(formula='high~low',data = df_ne)
        result = model.fit()

        # beta = low
        beta_rsquared[i + 1, 0] = result.params[1]
        beta_rsquared[i + 1, 1] = result.rsquared

    data[['beta', 'R2']] = beta_rsquared

    # 日收益率
    data['ret'] = data.close.pct_change(1)
    
    # 标准分
    #data['beta_norm'] = (data['beta'] - data.beta.rolling(M).mean().shift(1))
    #/ data.beta.rolling(M).std().shift(1)
    data['beta_norm'] = data['beta'].rolling(M).apply(lambda x:scs.zscore(x.values)[-1])

    beta = data.columns.get_loc('beta')
    beta_norm = data.columns.get_loc('beta_norm')
    data.iloc[:min(M, len(highs)), beta_norm] = scs.zscore(data.iloc[:min(M, len(highs)), beta].values)
    #beta_norm = data.columns.get_loc('beta_norm')
    #beta = data.columns.get_loc('beta')
    #for i in range(min(M, len(highs))):
    # data.iat[i, beta_norm] = (data.iat[i, beta] - data.iloc[:i - 1,
    # beta].mean()) / data.iloc[:i - 1, beta].std() if (data.iloc[:i - 1,
    # beta].std() != 0) else np.nan

    #data.iat[2, beta_norm] = 0
    data['RSRS_R2'] = data.beta_norm * data.R2
    data = data.fillna(0)
    
    # 右偏标准分
    data['beta_right'] = data.RSRS_R2 * data.beta

    return data


def buy_sell_fun(price, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    data = price.copy()
    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记
    data['hprice'] = 0  # 持仓价格
    bflag = data.columns.get_loc('bflg')
    # beta = data.columns.get_loc('beta')
    flag = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')
    close_col = data.columns.get_loc('close')
    open_col = data.columns.get_loc('open')
    hprice_col = data.columns.get_loc('hprice')
    position = 0 # 是否持仓，持仓：1，不持仓：0
    for i in range(1,data.shape[0] - 1):
        # 开仓
        if data.iat[i, bflag] > 0 and position == 0:
            data.iat[i + 1, flag] = 1
            data.iat[i + 1, position_col] = 1
            data.iat[i + 1, hprice_col] = data.iat[i+1, open_col]
            position = 1
            print("buy  : date=%s code=%s price=%.2f" % (data.iloc[i+1].name[0], data.iloc[i+1].name[1], data.iloc[i+1].close))
        # 平仓
        # elif data.iat[i, bflag] == S2 and position == 1:
        elif data.iat[i, position_col] > 0 and position == 1:
            cprice = data.iat[i, close_col]
            # oprice = data.iat[i, open_col]
            hprice = data.iat[i, hprice_col]
            if cprice < hprice * 0.95 or cprice > hprice * 1.2:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hprice_col] = 0
                position = 0
                print("sell : code=%s date=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
            else:
                data.iat[i + 1, position_col] = data.iat[i, position_col]
                data.iat[i + 1, hprice_col] = data.iat[i, hprice_col]
        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]
            data.iat[i + 1, hprice_col] = data.iat[i, hprice_col]

    data['nav'] = (1+data.close.pct_change(1).fillna(0) * data.position).cumprod()
    return data

def buy_sell_fun_mp(datam, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    dataR = pd.DataFrame()
    for code in datam.index.levels[1]:
        # data = price.copy()
        price = datam.query("code=='%s'" % code)
        data = price.copy()
        data = buy_sell_fun(data)
        # if code == '000732':
        #     print(data.tail(22))
        if len(dataR) == 0:
            dataR = data
        else:
            dataR = dataR.append(data)



    result01 = dataR['nav'].groupby(level=['date']).sum()
    result02 = dataR['nav'].groupby(level=['date']).count()

    num = dataR.flag.abs().sum()
    dataR2 = pd.DataFrame({'nav':result01 - result02 + 1,'flag':0})
    # dataR2['flag'] = 0
    dataR2.iat[-1,1] = num
    # result['nav'] = result['nav']  - len(datam.index.levels[1]) + 1
    return dataR2

def get_data(st_start):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    codelist = ['512690', '510900', '513100', '510300',
                '512980', '512170', '515000', '512800',
                '159941', '159994', '515050', '159920',
                '159952', '159987', '159805', '159997',
                '159919',]

    codelist = ['510300']

    # 获取ETF/股票中文名称，只是为了看得方便，交易策略并不需要ETF/股票中文名称
    #stock_names = QA.QA_fetch_etf_name(codelist)
    #codename = [stock_names.at[code, 'name'] for code in codelist]

    ## 读取 ETF基金 日线，存在index_day中
    #data_day = QA.QA_fetch_index_day_adv(codelist,
    #    start='2010-01-01',
    #    end='{}'.format(datetime.date.today()))

    # codelist = ['600519']
    #codelist = ['600239']
    #codelist = ['600338']
    codelist = ['600095','600822','600183']
    codelist = ["600109", "600551", "600697", "601066", "000732", "000905", "002827","600338","002049","300620"]
    # codelist = ['600380','600822']

    code_file = "../config/stock3_list.json"
    codelist = []
    with open(code_file, 'r') as f:
        data = json.load(f)
        for d in data['code']:
            if len(d) > 6:
                d = d[len(d) - 6:len(d)]
            codelist.append(d)

    # print("code list", codelist)
    # 获取股票中文名称，只是为了看得方便，交易策略并不需要股票中文名称
    # stock_names = QA.QA_fetch_stock_name(codelist)
    # codename = [stock_names.at[code] for code in codelist]

    # data_day = QA.QA_fetch_stock_day_adv(codelist,
    #                                     '2010-01-01',
    #                                     '{}'.format(datetime.date.today(),)).to_qfq()
    # st_start="2018-12-01"
    data_day = mongo.get_stock_day(codelist, st_start=st_start)

    end_t = datetime.datetime.now()
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))

    return data_day

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)

    # # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['512690', '510900', '513100', '510300',
    #             '512980', '512170', '515000', '512800',
    #             '159941', '159994', '515050', '159920',
    #             '159952', '159987', '159805', '159997',
    #             '159919',]
    #
    # codelist = ['510300']
    #
    # # 获取ETF/股票中文名称，只是为了看得方便，交易策略并不需要ETF/股票中文名称
    # #stock_names = QA.QA_fetch_etf_name(codelist)
    # #codename = [stock_names.at[code, 'name'] for code in codelist]
    #
    # ## 读取 ETF基金 日线，存在index_day中
    # #data_day = QA.QA_fetch_index_day_adv(codelist,
    # #    start='2010-01-01',
    # #    end='{}'.format(datetime.date.today()))
    #
    # # codelist = ['600519']
    # #codelist = ['600239']
    # #codelist = ['600338']
    # codelist = ['600095','600822','600183']
    # codelist = ["600109", "600551", "600697", "601066", "000732", "000905", "002827","600338","002049","300620"]
    # # codelist = ['600380','600822']
    #
    # code_file = "../config/stock3_list.json"
    # codelist = []
    # with open(code_file, 'r') as f:
    #     data = json.load(f)
    #     for d in data['code']:
    #         if len(d) > 6:
    #             d = d[len(d) - 6:len(d)]
    #         codelist.append(d)
    #
    # # print("code list", codelist)
    # # 获取股票中文名称，只是为了看得方便，交易策略并不需要股票中文名称
    # # stock_names = QA.QA_fetch_stock_name(codelist)
    # # codename = [stock_names.at[code] for code in codelist]
    #
    # # data_day = QA.QA_fetch_stock_day_adv(codelist,
    # #                                     '2010-01-01',
    # #                                     '{}'.format(datetime.date.today(),)).to_qfq()
    st_start="2018-12-01"
    data_day = get_data(st_start)
    indices_rsrsT = tdx_func(data_day)
    resultT = buy_sell_fun_mp(indices_rsrsT)
    num = resultT.flag.abs().sum() / 2
    nav = resultT.nav[resultT.shape[0] - 1]
    mnav = min(resultT.nav)
    print('RSRS1_T 交易次数 = ',num)
    print('策略净值为= %.2f 最大回撤 %.2f ' % (nav, (1 - mnav) * 100))

    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))

    benchcode = "000300"
    result = mongo.get_index_day(benchcode, st_start=st_start)
    # indices_rsrs = data_day.add_func(pre_rsrs_data_func)
    # result = indices_rsrs
    # print(indices_rsrs)

    #xtick = np.arange(0,result.shape[0],int(result.shape[0] / 7))
    #xticklabel = pd.Series(result.index.date[xtick])
    xticklabel = result.index.get_level_values(level=0).to_series().apply(lambda x: x.strftime("%Y-%m-%d")[2:16])

    # TODO
    plt.figure(figsize=(15,3))
    fig = plt.axes()
    plt.plot(np.arange(resultT.shape[0]), resultT.nav,label = 'MyCodes',linewidth = 2)
    # plt.plot(np.arange(result.shape[0]), result2.nav,label = 'RSRS2',linewidth = 2)
    # plt.plot(np.arange(result.shape[0]), result3.nav,label = 'RSRS3',linewidth = 2)
    # plt.plot(np.arange(result.shape[0]), result4.nav,label = 'RSRS4',linewidth = 2)
    plt.plot(np.arange(result.shape[0]), result.close / result.close[0], label = benchcode, linewidth = 2)

    fig.set_xticks(range(0, len(xticklabel),
                         round(len(xticklabel) / 12)))
    fig.set_xticklabels(xticklabel[::round(len(xticklabel) / 12)],
                        rotation = 45)
    plt.legend()
    plt.show()