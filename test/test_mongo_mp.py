from easyquant import MongoIo
from multiprocessing import Pool
import time

# mongo=MongoIo()
PAGE_SUM=100
def to_mongo_pool(pageNum):
    # pass
    mongo = MongoIo()
    # print("teset")
    data={"positionId":pageNum, "data":"data=%d" % pageNum}
    save_to_mongo(mongo, data)

def save_to_mongo(mongo, data):
    db = mongo.db
    if db["test-mp"].update_one({'positionId': data['positionId']}, {'$set': data}, True):
        print('Saved to Mongo', data['positionId'])
    else:
        print('Saved to Mongo Failed', data['positionId'])

start_time = time.time()
pool = Pool()

pool.map(to_mongo_pool,[i for i in range(PAGE_SUM)])

pool.close()

pool.join()

end_time = time.time()

print("总耗费时间%.2f秒" % (end_time - start_time))