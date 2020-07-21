
import pandas as pd

def new_df(df_day, data, now_price):
    code = data['code']
    now_vol = data['volume']
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