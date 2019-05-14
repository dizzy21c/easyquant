#import easyquant.qafetch.QATdx as tdx
import testczsc
a=testczsc.ChanMain('000001')
a.func1()
#print(a.data_df)
pin=list(a.data_df['out'])
a.func2(pin)

print(a.data_df)


#tdx.select_best_ip()
#a=tdx.QA_fetch_get_stock_latest('000977')
#print(a)

