import pandas as pd

class DataUtil:
    def __init__ (self):
        pass

    def series(self, data):
        pd.Series({'close':data['close'], 'open':data['open'], 'low':data['low'], 'high':data['high'], 'vol':data['vol']})