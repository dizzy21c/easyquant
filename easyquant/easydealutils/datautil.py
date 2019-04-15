import pandas as pd

class DataUtil:
    def __init__ (self):
        pass

    def series(self, data):
        pd.Series({'close':data['close'], 'open':data['open'], 'low':data['low'], 'high':data['high'], 'vol':data['vol']})
    
    def day_summary(self, data, rtn={}):
        pc = data['close']
        c = data['now'] 
        if c == 0 or pc == 0:
            return rtn

        pct = (c - pc) * 100 / pc
        if rtn == {}:
            rtn['utop'] = 0
            rtn['dtop'] = 0

            rtn['u6-9'] = 0
            rtn['u3-6'] = 0
            rtn['u0-3'] = 0

            rtn['d0-3'] = 0
            rtn['d3-6'] = 0
            rtn['d6-9'] = 0

            rtn['up'] = 0
            rtn['down'] = 0

            if pct < 0:
                rtn['down'] = rtn['down'] + 1
            else:
                rtn['up'] = rtn['up'] + 1

            if pct >= 0 and pct < 3:
                rtn['u0-3'] = rtn['u0-3'] + 1

            if pct >= 3 and pct < 6:
                rtn['u3-6'] = rtn['u3-6'] + 1

            if pct >= 6 and pct <= 9.9:
                rtn['u6-9'] = rtn['u6-9'] + 1

            if pct > 9.9 and pct < 50:
                rtn['utop'] = rtn['utop'] + 1

            if pct < 0 and pct > -3:
                rtn['d0-3'] = rtn['d0-3'] + 1

            if pct <= -3 and pct > -6:
                rtn['d3-6'] = rtn['d3-6'] + 1

            if pct <= -6 and pct >= -9.9:
                rtn['d6-9'] = rtn['d6-9'] + 1

            if pct < -9.9:
                rtn['dtop'] = rtn['dtop'] + 1
        else:
            if pct < 0:
                rtn['down'] = rtn['down'] + 1
            else:
                rtn['up'] = rtn['up'] + 1

            if pct >= 0 and pct < 3:
                rtn['u0-3'] = rtn['u0-3'] + 1

            if pct >= 3 and pct < 6:
                rtn['u3-6'] = rtn['u3-6'] + 1

            if pct >= 6 and pct <= 9.9:
                rtn['u6-9'] = rtn['u6-9'] + 1

            if pct > 9.9 and pct < 50:
                rtn['utop'] = rtn['utop'] + 1

            if pct < 0 and pct > -3:
                rtn['d0-3'] = rtn['d0-3'] + 1

            if pct <= -3 and pct > -6:
                rtn['d3-6'] = rtn['d3-6'] + 1

            if pct <= -6 and pct >= -9.9:
                rtn['d6-9'] = rtn['d6-9'] + 1

            if pct < -9.9:
                rtn['dtop'] = rtn['dtop'] + 1

        return rtn
