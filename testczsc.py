# import pymongo
# import redis
from threading import Thread

from easyquant import RedisIo

class Centroid:

  def __init__(self):
    self.bValid = False
    self.nTop1  = 0
    self.nTop2  = 0
    self.nBot1  = 0
    self.nBot2  = 0
    self.fTop1  = 0
    self.fTop2  = 0
    self.fBot1  = 0
    self.fBot2  = 0
    self.nLines = 0
    self.nStart = 0
    self.nEnd   = 0
    self.fHigh  = 0
    self.fLow   = 0
    self.fPHigh = 0
    self.fPLow  = 0    

  def PushHigh(self, nIndex, fValue):
    # 推入高点并计算状态
    if (self.bValid == True):
      self.nLines = self.nLines + 1
      self.fPHigh = self.fHigh
      self.fPLow  = self.fLow
    else:
      self.nLines = 0

    # 更新高低点位置信息
    self.nTop2 = self.nTop1
    self.fTop2 = self.fTop1
    self.nTop1 = nIndex
    self.fTop1 = fValue

  # 如果非中枢模式下
    if (self.bValid == False):
      # 更新中枢高
      if (self.fTop1 < self.fTop2):
        self.fHigh  = self.fTop1
      else:
        self.fHigh  = self.fTop2

      # 中枢识别
      if (self.fHigh > self.fLow):
        if  (self.fBot1 < self.fBot2):
          self.nStart = self.nBot2
        else:
          self.nStart = self.nTop2
        self.bValid = True
    # 如果在中枢中
    else:
     # 更新中枢高
      if (self.fHigh > self.fTop1):
        self.fHigh  = self.fTop1

      # 中枢终结
      if (self.fHigh < self.fLow):
        self.fHigh  = self.fTop1
        self.fLow   = self.fBot1
        self.nEnd   = self.nTop2
        self.bValid = False

        if (self.nLines > 2):
          return True

    return False

  def PushLow(self, nIndex, fValue):
    if (self.bValid == True):
      self.nLines = self.nLines + 1
      self.fPLow  = self.fLow
      self.fPHigh = self.fHigh
    else:
      self.nLines = 0

    # 更新定位信息
    self.nBot2 = self.nBot1
    self.fBot2 = self.fBot1
    self.nBot1 = nIndex
    self.fBot1 = fValue

    # 如果非中枢模式下
    if (self.bValid == False):
      # 更新区间低点
      if (self.fBot1 > self.fBot2):
        self.fLow = self.fBot1
      else:
        self.fLow = self.fBot2

      # 中枢捕捉
      if (self.fHigh > self.fLow):
        if (self.fTop1 > self.fTop2):
          self.nStart = self.nTop2
        else:
          self.nStart = self.nBot2
        self.bValid = True
    # 如果在中枢中
    else:
      # 更新中枢低
      if (self.fLow < self.fBot1):
        self.fLow = self.fBot1

      # 中枢终结
      if (self.fHigh < self.fLow):
        self.fHigh  = self.fTop1
        self.fLow   = self.fBot1
        self.nEnd   = self.nBot2
        self.bValid = False

        if (self.nLines > 2):
          return True

    return False


# *****************************************************************************
# 禅论可视化分析系统
# Copyright (C) 2016, Martin Tang
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http:#www.gnu.org/licenses/>.
#  *****************************************************************************/

#include "Main.h"

#=============================================================================
# 数学函数部分
#=============================================================================
class ChanMain:
  def __init__(self, code):
    self.code = code
    r = RedisIo('redis.conf')
    self.data_df = r.get_day_df(code)
    self.data_df['out'] = 0
    self.data_df['out_high'] = 0
    self.data_df['out_low'] = 0
    self.data_df['zs_flg'] = 0
    self.data_df['bs_flg'] = 0
    # pass

  def init_data(self, redis):
    self.data_df = redis.get_day_df(self.code)
    self.data_df['out'] = 0

  def set_out(self,index, value):
    self.data_df.loc[index,'out'] = value

  def set_out_high(self,index, value):
    self.data_df.loc[index,'out_high'] = value

  def set_out_low(self,index, value):
    self.data_df.loc[index,'out_low'] = value

  def set_zs_flg(self,index1, index2):
    self.data_df.loc[index1,'zs_flg'] = 1
    self.data_df.loc[index2,'zs_flg'] = 2

  def set_3lmm_flg(self,index, value):
    self.data_df.loc[index,'bs_flg'] = value

  def out(self, index):
    return self.data_df.loc[index]['out']

  def low(self, index):
    return self.data_df.loc[index]['low']

  def high(self, index):
    return self.data_df.loc[index]['high']

  def check_span(self, j, nSpan):
    if ((self.high(j) >= self.high(j+1)) and (self.low(j) <= self.low(j+1))):
      nSpan = nSpan - 1
    elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
      nSpan = nSpan - 1
    return nSpan

  # 顶底扫描定位函数
  def pd_parse1(self): #nCount,  pOut,  pHigh,  pLow):
    # data_df['out'] = 0
    nCount = len(self.data_df)
    nState = -1
    nHigh  = 0
    nLow   = 0

    for index in range(1, nCount):
    # for index, row in data_df.iterrows():
      # 寻找高点模式
      if (nState == 1):
        # 如果当前最高大于之前最高，更新位置信息
        # if (pHigh[i] >= pHigh[nHigh]):
        #   pOut[nHigh] = 0;
        #   nHigh = i;
        #   pOut[nHigh] = 1;
        fcHigh = self.high(index)
        fpHigh = self.high(nHigh)
        if fcHigh >= fpHigh:
          self.set_out(nHigh, 0)
          nHigh = index
          self.set_out(nHigh, 1)
        # nHigh = self.check_high(index, nHigh)

        # 确认转向（原文：当前最高小于高点最低，当前最低小于高点最低）
        # if ((pHigh[i] < pHigh[nHigh]) and (pLow[i]  < pLow[nHigh])):
        #   pOut[nHigh] = 1;
        #   nState = -1;
        #   nLow   = i;
        fcLow = self.low(index)
        fpLow = self.low(nHigh)
        if fcHigh < fpHigh and fcLow < fpLow:
          self.set_out(nHigh, 1)
          nState = -1
          nLow = index
      # 寻找低点模式
      elif (nState == -1):
        # 如果当前最低小于之前最低，更新位置信息
        fcLow = self.low(index)
        fpLow = self.low(nLow)
        if fcLow <= fpLow:
        # if (pLow[i] <= pLow[nLow]):
          self.set_out(nLow, 0)
          # pOut[nLow] = 0;
          nLow = index
          # pOut[nLow] = -1;
          self.set_out(nLow, 1)

        # 确认转向（原文：当前最高大于高点最低，当前最低大于高点最低）
        fcHigh = self.high(index)
        fpHigh = self.high(nLow)
        if fcLow > fpLow and fcHigh > fpHigh:
        # if ((pLow[i]  > pLow[nLow]) and (pHigh[i] > pHigh[nLow])):
          # pOut[nLow] = -1;
          self.set_out(nLow, -1)

          nState = 1
          nHigh  = index

    # 化简函数（至少5根K线完成一笔）
  def pd_parse2(self): #, nCount,  pOut,  pHigh,  pLow):
    nSpan = 0
    nCurrTop = 0
    nPrevTop = 0
    nCurrBot = 0
    nPrevBot = 0
    nCount = len(self.data_df)

    for i in range(0, nCount):
    # for (int i = 0; i < nCount; i++):
      # 遇到高点，合并化简上升段（上下上）
      if (self.out(i) == 1):
        # 更新位置信息
        nPrevTop = nCurrTop
        nCurrTop = i

        # 存在小于五根的线段，去除中间一段
        if self.high(nCurrTop) >= self.high(nPrevTop) and self.low(nCurrBot) > self.low(nPrevBot):
        # if ((pHigh[nCurrTop] >= pHigh[nPrevTop]) and (pLow [nCurrBot] >  pLow [nPrevBot])):
          # 检查合法性（严格按照连续五根形成一笔）
          if (((nCurrTop - nCurrBot < 4) and (nCount   - nCurrTop > 4)) or
              (nCurrBot - nPrevTop < 4) or (nPrevTop - nPrevBot < 4)):
            self.set_out(nCurrBot, 0)
            self.set_out(nPrevTop, 0)
            # pOut[nCurrBot] = 0;
            # pOut[nPrevTop] = 0;
          elif (nCount - nCurrTop > 4):
            # 检查第三段（上）K线合并
            nSpan = nCurrTop - nCurrBot
            for j in range(nCurrBot, nCurrTop):
            # for (int j = nCurrBot; j < nCurrTop; j++):
              if (self.high(j) >= self.high(j+1) and self.low(j) <= self.low(j+1)):
                nSpan = nSpan - 1
              elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
                nSpan = nSpan - 1
                # nSpan--;
            if (nSpan < 4):
              self.set_out(nCurrBot, 0)
              self.set_out(nPrevTop, 0)

            # 检查第二段（下）K线合并
            nSpan = nCurrBot - nPrevTop
            for j in range(nPrevTop,nCurrBot):
            # for (int j = nPrevTop; j < nCurrBot; j++):
              if (self.high(j) >= self.high(j+1) and self.low(j) <= self.low(j+1)):
                nSpan = nSpan - 1
              elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
                nSpan = nSpan - 1
            if (nSpan < 4):
              self.set_out(nCurrBot, 0)
              self.set_out(nPrevTop, 0)

            # 检查第一段（上）K线合并
            nSpan = nPrevTop - nPrevBot
            for j in range(nPrevBot, nPrevTop):
            # for (int j = nPrevBot; j < nPrevTop; j++):
              if (self.high(j) >= self.high(j+1) and self.low(j) <= self.low(j+1)):
                nSpan = nSpan - 1
              elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
                nSpan = nSpan - 1
            if (nSpan < 4):
              self.set_out(nCurrBot, 0)
              self.set_out(nPrevTop, 0)

      # 遇到低点，合并化简下降段（下上下）
      if (self.out(i) == -1):
        # 更新位置信息
        nPrevBot = nCurrBot
        nCurrBot = i

        # 存在小于五根的线段，去除中间一段
        if (self.low (nCurrBot) <= self.low (nPrevBot)) and (self.high(nCurrTop) <  self.high(nPrevTop)):
          # 检查合法性（严格按照连续五根形成一笔）
          if (((nCurrBot - nCurrTop < 4) and (nCount   - nCurrBot > 4)) or
              (nCurrTop - nPrevBot < 4) or (nPrevBot - nPrevTop < 4)):
            self.set_out(nCurrTop, 0)
            self.set_out(nPrevBot, 0)
          elif (nCount - nCurrBot > 4):
            # 检查第三段（下）K线合并
            nSpan = nCurrBot - nCurrTop
            for j in range(nCurrTop, nCurrBot):
            # for (int j = nCurrTop; j < nCurrBot; j++):
              if ((self.high(j) >= self.high(j+1)) and (self.low(j) <= self.low(j+1))):
                nSpan = nSpan - 1
              elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
                nSpan = nSpan - 1
            if (nSpan < 4):
              self.set_out(nCurrTop, 0)
              self.set_out(nPrevBot, 0)

            # 检查第二段（上）K线合并
            nSpan = nCurrTop - nPrevBot
            for j in range(nPrevBot, nCurrTop):
            # for (int j = nPrevBot; j < nCurrTop; j++):
              if ((self.high(j) >= self.high(j+1)) and (self.low(j) <= self.low(j+1))):
                nSpan = nSpan - 1
              elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
                nSpan = nSpan - 1
            if (nSpan < 4):
              self.set_out(nCurrTop, 0)
              self.set_out(nPrevBot, 0)

            # 检查第一段（下）K线合并
            nSpan = nPrevBot - nPrevTop
            for j in range(nPrevTop, nPrevBot):
            # for (int j = nPrevTop; j < nPrevBot; j++):
              if ((self.high(j) >= self.high(j+1)) and (self.low(j) <= self.low(j+1))):
                nSpan = nSpan - 1
              elif (self.high(j) < self.high(j+1) and self.low(j) > self.low(j+1)):
                nSpan = nSpan - 1
            if (nSpan < 4):
              self.set_out(nCurrTop, 0)
              self.set_out(nPrevBot, 0)

  def func1(self, nTime=2):
    self.pd_parse1()
    for i in range(0, nTime):
      self.pd_parse2()

  # #=============================================================================
  # # 输出函数2号：中枢高点数据
  # #=============================================================================

  def func2(self, pIn):
    centroid = Centroid()
    nCount = len(self.data_df)
    for i in range(0, nCount):
    # for (int i = 0; i < nCount; i++):
      if (pIn[i] == 1):
        # 遇到线段高点，推入中枢算法
        if (centroid.PushHigh(i, self.high(i))):
          # 区段内更新算得的中枢高数据
          self.set_zs_flg(centroid.nStart, centroid.nEnd)
          self.set_3lmm_flg(i, 13)
          for j in range(centroid.nStart, centroid.nEnd):
          # for (int j = centroid.nStart; j <= Centroid.nEnd; j++):
            # pOut[j] = centroid.fPHigh;
            self.set_out_high(j, centroid.fPHigh)
            self.set_out_low(j, centroid.fPLow)
        elif (centroid.fTop1 < centroid.fTop2):
          self.set_3lmm_flg(i,12)
        # else:
        #   self.set_3lmm_flg(i,0)
      elif (pIn[i] == -1):
        # 遇到线段低点，推入中枢算法
        if (centroid.PushLow(i, self.low(i))):
          self.set_zs_flg(centroid.nStart, centroid.nEnd)
          self.set_3lmm_flg(i, 3)
          # 区段内更新算得的中枢低数据
          for j in range(centroid.nStart, centroid.nEnd):
          # for (int j = Centroid.nStart; j <= Centroid.nEnd; j++):
            # pOut[j] = Centroid.fPHigh;
            self.set_out_high(j, centroid.fPHigh)
            self.set_out_low(j, centroid.fPLow)
        elif (centroid.fBot1 > centroid.fBot2):
          self.set_3lmm_flg(i, 2)
        # else:
        #   self.set_3lmm_flg(i,0)

      # 尾部未完成中枢处理
      if (centroid.bValid and (centroid.nLines >= 2) and (i == nCount - 1)):
        self.set_zs_flg(centroid.nStart, nCount - 1)
        for j in range(centroid.nStart, nCount):
        # for (int j = Centroid.nStart; j < nCount; j++):
          # pOut[j] = Centroid.fHigh;
          self.set_out_high(j, centroid.fHigh)
          self.set_out_low(j, centroid.fLow)

  # #=============================================================================
  # # 输出函数6号：形态买卖点信号
  # #=============================================================================

  # def func6(nCount,  pOut,  pIn,  pHigh,  pLow):
  #   float fTop1 = 0, fTop2 = 0, fTop3 = 0, fTop4 = 0;
  #   float fBot1 = 0, fBot2 = 0, fBot3 = 0, fBot4 = 0;

  #   for (int i = 0; i < nCount; i++):
  #     if (pIn[i] == 1):
  #       fTop4 = fTop3;
  #       fTop3 = fTop2;
  #       fTop2 = fTop1;
  #       fTop1 = pHigh[i];

  #       if (((fBot1 - fTop2)/fTop2 > (fBot2 - fTop3)/fTop3) and
  #           ((fBot2 - fTop3)/fTop3 > (fBot3 - fTop4)/fTop4)):
  #         if ((fBot1 < fBot2) and (fTop2 < fTop3) and
  #             (fBot2 < fBot3) and (fTop3 < fTop4)):
  #           pOut[i] = 1;
  #           continue;
  #         if ((fBot1 > fBot2) and (fTop2 > fTop3) and (fBot2 < fBot3) and
  #             (fTop3 < fTop4) and (fBot1 < fTop3)):
  #           pOut[i] = 2;
  #           continue;
  #         if ((fBot1 > fTop3) and (fBot2 > fBot3) and (fTop3 > fTop4)):
  #           pOut[i] = 3;
  #           continue;
  #     else if (pIn[i] == -1):
  #       fBot4 = fBot3;
  #       fBot3 = fBot2;
  #       fBot2 = fBot1;
  #       fBot1 = pLow[i];

  #       if (((fBot1 - fTop1)/fTop1 > (fBot2 - fTop2)/fTop2) and
  #           ((fBot2 - fTop2)/fTop2 > (fBot3 - fTop3)/fTop3)):
  #         if ((fBot1 < fBot2) and (fTop1 < fTop2) and
  #             (fBot2 < fBot3) and (fTop2 < fTop3)):
  #           pOut[i] = 1;
  #           continue;
  #         if ((fBot1 > fBot2) and (fTop1 > fTop2) and (fBot2 < fBot3) and
  #             (fTop2 < fTop3) and (fBot1 < fTop2)):
  #           pOut[i] = 2;
  #           continue;
  #         if ((fBot1 > fTop2) and (fBot2 > fBot3) and (fTop2 > fTop3)):
  #           pOut[i] = 3;
  #           continue;
  #     else:
  #       pOut[i] = 0;

  # #=============================================================================
  # # 输出函数7号：线段强度分析指标
  # #=============================================================================

  # def func7(nCount,  pOut,  pIn,  pHigh,  pLow):
  #   nPrevTop = 0, nPrevBot = 0;

  #   for (int i = 0; i < nCount; i++):
  #     # 遇到线段高点
  #     if (pIn[i-1] == 1):
  #       # 标记高点位置
  #       nPrevTop = i - 1;
  #     # 遇到线段低点
  #     else if (pIn[i-1] == -1):
  #       # 标记低点位置
  #       nPrevBot = i - 1;

  #     # 上升线段计算模式
  #     if (pIn[i] == 1):
  #       # 计算上升线段斜率
  #       pOut[i] = (pHigh[i] - pLow[nPrevBot]) / pLow[nPrevBot]# 100;
  #     # 下降线段计算模式
  #     else if (pIn[i] == -1):
  #       # 计算上升线段斜率
  #       pOut[i] = (pLow[i] - pHigh[nPrevTop]) / pHigh[nPrevTop]# 100;

  # #=============================================================================
  # # 输出函数8号：线段斜率分析指标
  # #=============================================================================

  # def func8(nCount,  pOut,  pIn,  pHigh,  pLow):
  #   nPrevTop = 0, nPrevBot = 0;

  #   for (int i = 0; i < nCount; i++):
  #     # 遇到线段高点
  #     if (pIn[i-1] == 1):
  #       # 标记高点位置
  #       nPrevTop = i - 1;
  #     # 遇到线段低点
  #     else if (pIn[i-1] == -1):
  #       # 标记低点位置
  #       nPrevBot = i - 1;

  #     # 上升线段计算模式
  #     if (pIn[i] == 1):
  #       # 计算上升线段斜率
  #       pOut[i] = (pHigh[i] - pLow[nPrevBot]) / (i - nPrevBot);
  #     # 下降线段计算模式
  #     else if (pIn[i] == -1):
  #       # 计算上升线段斜率
  #       pOut[i] = (pLow[i] - pHigh[nPrevTop]) / (i - nPrevTop);

def main():
  # pass
  c = Centroid()
  c.PushHigh(0, 1)
  c.PushLow(1,2)
    # ri = RedisIo('redis.conf')
    # ri.lookup_redis_info()
    # ri.set_key_value('test1', 1)
    # ri.push_list_value('test2', 1)
    # ri.push_list_value('test2', 2)

if __name__ == '__main__':
  main()
