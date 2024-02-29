#回测策略：龙头战法,计算与最高点的回撤程度，当回撤超过一定阈值就半仓
import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
from utils.increase import getIncrease
from  utils.judgeBurst import judgeBurst
import pychrome
import math
from colorama import Fore, Back, Style

# 指定回测年份
year = 2024
#初始资金
money = 100000
#初始建议仓位
suggest_shipping_space = 1
#资金记录
stockLog = []
#交易日期
dates = []
#是否输出策略分析
forecast = False
if '/backtest' in os.getcwd():
   forecast = True

# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stock_log_data.json', 'r',) as file:
        dragon_log_data = json.load(file)
except FileNotFoundError:
    dragon_log_data = []
stockPool = []
#股票池
if len(dragon_log_data) != 0 and 'stock' in dragon_log_data[-1]:
   stockPool =  [dragon_log_data[-1]['stock']]
if len(dragon_log_data) != 0:
   suggest_shipping_space =  dragon_log_data[-1]['suggest_shipping_space']

#检查是否为涨停以来最大换手率
def isBigestChangeHands(date,buyStock):
    for index, item in enumerate(stocks_data): 
                if item['date'] == date:
                    startIndex = index - buyStock['limit'] + 2
                    break
    if startIndex < 0:
       return False
    currentHuanShou = float(buyStock['limit_liu_ratio'].replace(",", ""))/float(buyStock['limit_cheng_ratio'].replace(",", ""))*100
    maxHuanShou = 0
    for index,item in enumerate(stocks_data[startIndex:]): 
        for item2 in item['data']:
            if item2['code'] == buyStock['code']:
                itemHuanShou = float(item2['limit_liu_ratio'].replace(",", ""))/float(item2['limit_cheng_ratio'].replace(",", ""))*100
                if maxHuanShou < itemHuanShou:
                    maxHuanShou = itemHuanShou
                break
    return currentHuanShou == maxHuanShou

def formartNumber(earnings):
    return math.floor(earnings * 100) / 100

def getTodayStock(todayStocks, exchangeStock):
    for stock in todayStocks:
        if stock['code'] == exchangeStock['code']:
            updateStock = stock
            return updateStock

    return exchangeStock

def isEarly(first_limit_time, compared_time):
    # 将字符串转换为时间对象
    first_limit_datetime = datetime.strptime(first_limit_time, '%H:%M:%S')
    compared_datetime = datetime.strptime(compared_time, '%H:%M:%S')
    # 比较时间
    return first_limit_datetime <= compared_datetime

def isAfter(first_limit_time, compared_time):
    # 将字符串转换为时间对象
    first_limit_datetime = datetime.strptime(first_limit_time, '%H:%M:%S')
    compared_datetime = datetime.strptime(compared_time, '%H:%M:%S')
    # 比较时间
    return first_limit_datetime > compared_datetime

# 定义一个比较函数，用于比较股票的涨幅
def get_max_increase_stocks(stocks):
    # 初始化最大涨幅列表
    max_increase_stocks = []
    # 初始化最大涨幅值
    max_increase_value = None
    # 遍历股票列表
    for stock in stocks:
        increase = float(stock['next_opening_increase'].strip('%'))
        # 如果当前股票的涨幅大于最大涨幅值，更新最大涨幅值和列表
        if max_increase_value is None or increase > max_increase_value:
            max_increase_value = increase
            max_increase_stocks = [stock]
        # 如果当前股票的涨幅等于最大涨幅值，将其添加到列表中
        elif increase == max_increase_value:
            max_increase_stocks.append(stock)
    # 返回最大涨幅的股票列表
    return max_increase_stocks

#筛选当日有上板动作且昨日不是一字涨停的股票
def filter_limit(stocks):
    # 初始化筛选结果列表
    filtered_stocks = []
    # 遍历股票列表
    for stock in stocks:
        # 检查是否 next_isLimitUp 或 next_isBurst 为 True
        if (stock['next_isLimitUp'] or stock['next_isBurst'])  and '一字涨停' not in stock['limit_type']  and 'T字涨停' not in stock['limit_type'] and float(stock['close_increase'].strip('%')) > 9:
            filtered_stocks.append(stock)

    # 返回筛选结果
    return filtered_stocks

# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()
with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_dragon_backtest_data.json', 'r') as file:
    dragon_backtest_data = json.load(file)

for item in dragon_backtest_data:
    dates.append(item['date'])
dates = dates[len(dragon_log_data):]

for idx, date in enumerate(dates[1:]):
    # 获取上一个交易日
    pre_date = dates[idx]
    if len(dragon_log_data)>0:
        latestMoney = dragon_log_data[-1]['money']
    else:
        latestMoney = money
     #当前仓位
    if len(dragon_log_data) > 0:
       current_shipping_space = dragon_log_data[-1]['suggest_shipping_space']
    else:
       current_shipping_space = suggest_shipping_space
    #查询目标股
    for stocksData in dragon_backtest_data:
        if stocksData['date'] == pre_date:
            targetStocks = stocksData['data']
        if stocksData['date'] == date:
            todayStocks = stocksData['data']
    #如果此时空仓则可以执行以下买入操作
    if len(stockPool) == 0:
        #如果最板连板数大于2则主动空仓
        if True:
            # print(Style.RESET_ALL)
            print(date,'空仓')
            dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space})
            stockPool = []
        else:
            #排除当天一字涨停买不到的股票
            filtered_stocks = [stock for stock in targetStocks if not stock.get('next_isLimitUpNoBuy', False)]
            # 找到涨幅最高的股票
            max_increase_stock = get_max_increase_stocks(filtered_stocks)
            #筛选出有上板动作的股票
            focusSocks = filter_limit(max_increase_stock)
            if len(focusSocks) > 0:
                buyStock = focusSocks[0]
                if buyStock['next_isLimitUp']:
                    for stock in todayStocks:
                        if buyStock['code'] == stock['code']:
                           first_limit_time = stock['first_limit_time']
                           break
                #获取当日竞价信息,当日竞价幅度必须高于昨日否则空仓
                opening_increase = getOpeningIncrease(browserTab,date,buyStock['name'])
                #如果昨日出现最大换手且烂板则主动空仓
                if round(float(buyStock['opening_increase'] .strip('%'))) < round(float(opening_increase[0].strip('%'))) or len(targetStocks) > 1 and float(buyStock['opening_increase'].strip('%')) > 0:
                        #如果买入当日炸板,并且不能开盘就涨停,策略拒绝顶一字
                    if buyStock['next_isBurst'] and buyStock['next_burst_time'] !='09:30:00' and isEarly(buyStock['next_burst_time'],'11:30:00'):
                            increase = float(buyStock['next_close_increase'].strip('%'))
                            earnings = increase-10
                            #精确到小数点后面两位
                            earnings = formartNumber(earnings)
                            final_money = latestMoney + latestMoney * current_shipping_space * earnings/100
                            updateStock = getTodayStock(todayStocks,buyStock)
                            # print(f'{updateStock},{date}')
                            print(date,f'涨停打板买入{buyStock["name"]},结果炸板了,当日盈利{earnings}%,金额{round(final_money)},仓位{current_shipping_space}')
                            dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':f'{earnings}%','desc':f'涨停打板买入{ buyStock["name"]},结果炸板了,当日盈利{earnings}%','stock':updateStock,'suggest_shipping_space':current_shipping_space})
                            stockPool.append(updateStock)
                    elif buyStock['next_isLimitUp'] and isEarly(first_limit_time,'11:30:00'):
                        print(date,f'涨停打板买入{buyStock["name"]},当日盈利0%,金额{round(latestMoney)},仓位{current_shipping_space}')
                        updateStock = getTodayStock(todayStocks,buyStock)
                        # print(f'{updateStock},{date}')
                        dragon_log_data.append({'date':date, 'money':round(latestMoney), 'earnings':'0%','desc':f'涨停打板买入{buyStock["name"]}','stock':updateStock,'suggest_shipping_space':current_shipping_space})
                        stockPool.append(updateStock)
                    else:
                        print(date,'空仓')
                        dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space})
                        stockPool = []
                else:
                    print(date,'空仓')
                    dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space})
                    stockPool = []
            else:
                # 如果都是一字板没有机会就空仓
                print(date,'空仓')
                dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space})
                stockPool = []
    #卖出股票
    else:
        buyStock = stockPool[0]
        #获取当日竞价信息
        opening_increase = getOpeningIncrease(browserTab,date,buyStock['name'])
        next_opening_increase = float(opening_increase[0].strip('%'))
        #纠正错误的数据
        if next_opening_increase == -313:
           next_opening_increase = -3.13
        #如果昨日未出现炸板今日竞价低于0%则直接卖出
        if buyStock['next_isBurst'] and next_opening_increase < -3 or next_opening_increase < 0 and int(buyStock['limit_open_times'])  == 0 or next_opening_increase < -3 and int(buyStock['limit_open_times'])  > 0:
            #如果出现单笔交易不盈利情况则仓位减半
            if float(dragon_log_data[-1]['earnings'].strip('%')) <= 0:
                 next_shipping_space = 1
            #    next_shipping_space = current_shipping_space * 0.5
            #如果出现盈利，马上又推全仓
            else:
               next_shipping_space = 1
            next_opening_increase = formartNumber(next_opening_increase)
            final_money = latestMoney + latestMoney * current_shipping_space * next_opening_increase/100
            #清空股票池
            stockPool = []
            print(date,f'竞价卖出{buyStock["name"]},当日盈利{next_opening_increase}%,金额{round(final_money)}')
            dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':f'{next_opening_increase}%','desc':f'竞价卖出{buyStock["name"]},当日盈利{next_opening_increase}%','suggest_shipping_space':next_shipping_space})
        else:
            burstData = judgeBurst(browserTab,date,buyStock['code'])
            increase = getIncrease(browserTab,date,buyStock['name'])
            isLimit = buyStock['next_isLimitUp']
            #如果炸板则卖出
            if burstData[0]:
               stockPool = []
               final_money = latestMoney + latestMoney * current_shipping_space * 10/100
               print(date,f'炸板卖出{buyStock["name"]},当日盈利10%,金额{round(final_money)},仓位{current_shipping_space}')
               dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':'10%','desc':f'炸板卖出{buyStock["name"]},当日盈利10%','suggest_shipping_space':1})
            #如果没有炸板并且继续涨停则持有
            elif isLimit:
                updateStock = getTodayStock(todayStocks,buyStock)
                final_money = latestMoney + latestMoney * current_shipping_space * 10/100
                print(date,f'继续持有{buyStock["name"]},当日盈利10%,金额{round(final_money)},仓位{current_shipping_space}')
                stockPool = [updateStock]
                dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':'10%','desc':f'继续持有{buyStock["name"]},当日盈利10%','stock':updateStock,'suggest_shipping_space':current_shipping_space})
            #不涨停就卖出
            else:
               if float(dragon_log_data[-1]['earnings'].strip('%')) < 0:
                   next_shipping_space = 1
                #    next_shipping_space = current_shipping_space * 0.5
               else:
                   next_shipping_space = 1
               stockPool = []
               #如果竞价大于5%且开盘走势一路向上则有机会触摸涨停板，如果竞价收益为正且开盘后一路向下则跟随砸，如果竞价>-5%,开盘有机会上拉翻红出，止损点位位0%。
               earnings = float(buyStock['next_close_increase'].strip('%'))
               if earnings < 0:
                  earnings = 0
               final_money = latestMoney + latestMoney * current_shipping_space * earnings/100
               print(date,f'断板卖出{buyStock["name"]},当日盈利{earnings}%,金额{round(final_money)},仓位{current_shipping_space}')
               dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':f'{earnings}%','desc':f'断板卖出{buyStock["name"]},当日盈利{earnings}%','suggest_shipping_space':next_shipping_space})
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stock_log_data.json', 'w') as file:
        json.dump(dragon_log_data, file,ensure_ascii=False,  indent=4) 