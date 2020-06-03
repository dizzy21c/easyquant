import easyquotation
from datetime import datetime, date
import json
import easyquant
# from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine
from easyquant import PushBaseEngine
# from custom.fixedmainengine import FixedMainEngine


class SinaEngine(PushBaseEngine):
    # EventType = 'data-sina'
    # PushInterval = 10
    config = None

    def init(self):
        self.source = easyquotation.use('qq')  # sina, tencent/qq

    def fetch_quotation(self):
        if self.EventType == "worker":
            return []

        if self.config is None:
            return self.fetch_quotation_all()
        else:
            return self.fetch_quotation_config()

    def fetch_quotation_all(self):
        #print("fetch %s " % datetime.datetime.now())
        out = self.source.market_snapshot(prefix=True) 
        return out

    def fetch_quotation_config(self):
        config_name = './config/%s.json' % self.config
        with open(config_name, 'r') as f:
            data = json.load(f)
            out = self.source.stocks(data['code'])
            # print (out)
            while len(out) == 0:
                out = self.source.stocks(data['code'])
            # print (out)
            return out
            # return self.source.stocks(data['pos'])
