#回测策略：跟随资金强度战法,计算与最高点的回撤程度，当回撤超过一定阈值就半仓
import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
from  utils.judgeBurst import judgeBurst
from  utils.opening_limit import judgeOpeningLimit
import pychrome
import math
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup

# 指定回测年份
year = 2024
#初始资金
money = 100000
#初始建议仓位
suggest_shipping_space = 1
#资金记录
stockLog = []
#交易日期
origindates = []
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

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []

stockPool = []
#股票池
if len(dragon_log_data) != 0 and 'stock' in dragon_log_data[-1]:
   stockPool =  [dragon_log_data[-1]['stock']]
if len(dragon_log_data) != 0:
   suggest_shipping_space =  dragon_log_data[-1]['suggest_shipping_space']
if forecast:
   stockPool = []
def getJinLiang(date,code):
    browserTab.Page.navigate(url=f"https://www.iwencai.com/stockpick/search?rsh=3&typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={str(date)} {code}净量&queryarea=")
    browserTab.wait(3)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    div_content = soup.find_all('div', class_=['em', '_x_', 'alignRight'])
    # 检查是否找到元素，并提取文本
    if div_content:
        for div in div_content:
            if 'alignRight' in div['class']:
                jinliang = div.a.text.strip()
                return jinliang
    return ''

#检查是否为涨停以来的高换手率
def isHightChangeHands(date,buyStock):
    global stocks_data
    for index, item in enumerate(stocks_data): 
        if item['date'] == date:
            endIndex = index
            startIndex = index - buyStock['limit'] + 2
            break
    if startIndex < 0:
       return False
    currentHuanShou = float(buyStock['limit_liu_ratio'].replace(",", ""))/float(buyStock['limit_cheng_ratio'].replace(",", "").replace("万", ""))*100
    maxHuanShou = 0
    for index,item in enumerate(stocks_data[startIndex:endIndex]): 
        # print(f'😁-->>{item}-->>{buyStock["limit"]}-->>{buyStock["name"]}')
        for item2 in item['data']:
            if item2['code'] == buyStock['code']:
                itemHuanShou = float(item2['limit_liu_ratio'].replace(",", ""))/float(item2['limit_cheng_ratio'].replace(",", "").replace("万", ""))*100
                # print(f'😁换手{itemHuanShou}')
                if maxHuanShou < itemHuanShou:
                    maxHuanShou = itemHuanShou
                break
    # print(f'😁-->><{buyStock["name"]}-->>{buyStock["limit"]}-->>{currentHuanShou}-->>{maxHuanShou}-->{date}-->{stocks_data[startIndex]}')
    return currentHuanShou > maxHuanShou or abs(currentHuanShou - maxHuanShou) < 3

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

#筛选当日有上板动作且不是一字板的股票
def filter_limit(stocks):
    # 初始化筛选结果列表
    filtered_stocks = []
    # 遍历股票列表
    for stock in stocks:
        # 检查是否 next_isLimitUp 或 next_isBurst 为 True
        if (stock['next_isLimitUp'] or stock['next_isBurst']) and float(stock['close_increase'].strip('%')) > 9.5:
            filtered_stocks.append(stock)
    if forecast:
        return stocks
    else:
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
    origindates.append(item['date'])
dates = dates[len(dragon_log_data):]

# 从指定日期开始向前搜索上一个交易日
def get_previous_trading_day(date_object):
    if str(date_object) == '2023-01-03':
        return '2022-12-30'
    while True:
        date_object -= timedelta(days=1)  # 递减一天
        if str(date_object) in origindates:  # 如果是交易日，则返回该日期
            return date_object

def strategy(pre_date,date):
    global stockPool
    global forecast
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
        if stocksData['date'] == date and not forecast:
           todayStocks = stocksData['data']
    #如果此时空仓则可以执行以下买入操作
    if len(stockPool) == 0:
        #如果最板连板数大于或约等于3则主动空仓
        if len(targetStocks) > 3:
            reason = '1.最板连板数必须小于等于3;\n'
            print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
            print(Style.RESET_ALL)
            dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
            stockPool = []
        else:
            #排除当天开盘就一字涨停买不到的股票
            if not forecast:
                #如果目标个股有多个则排除竞价出来一字板的股票
                if len(targetStocks) > 1:
                    filtered_stocks = [stock for stock in targetStocks if not stock.get('next_isLimitUpNoBuy', False) and stock['next_burst_time'] != '09:30:00']
                #如果目标个股只有一个，只接受开盘竞价不涨停或者竞价封单很小的个股
                else:
                    filtered_stocks = [stock for stock in targetStocks if not stock.get('next_isLimitUpNoBuy', False) or 'open_limit_is_small' in stock and stock['open_limit_is_small']]
                limit_no_buy_stocks = [stock for stock in targetStocks if stock.get('next_isLimitUpNoBuy', True) or stock['next_burst_time'] == '09:30:00' and 'open_limit_is_small' not in stock]
            else:
                filtered_stocks = []
                limit_no_buy_stocks = []
                #判断是否竞价开盘就顶一字
                for item in targetStocks:
                    isOpenYiZi = judgeOpeningLimit(browserTab, date,item['code'])
                    if not isOpenYiZi:
                        filtered_stocks.append(item)
                    else:
                        limit_no_buy_stocks.append(item)
            # print(f'😁{limit_no_buy_stocks}')
            # 找到涨幅最高的股票
            max_increase_stock = get_max_increase_stocks(filtered_stocks)
            #筛选出有上板动作的股票
            focusSocks = filter_limit(max_increase_stock)
            # print(f'😁-->>max_increase_stock{max_increase_stock}')
            # print(f'😁-->>limit_no_buy_stocks{limit_no_buy_stocks}')
            # print(f'😁-->>focusSocks{focusSocks}')
            if len(focusSocks) > 0:
                buyStock = focusSocks[0]
                if forecast:
                   opening_increase = getOpeningIncrease(browserTab,date,buyStock['code'])
                   next_opening_increase = float(opening_increase[0].strip('%'))
                else:
                   next_opening_increase = float(buyStock['next_opening_increase'].strip('%'))

                # print(f'😁next_opening_increase->{next_opening_increase}')
                # print(f'😁-->>buyStock{buyStock}')
                #高换手且次日没有出现竞价大幅高开情况则主动空仓
                _preDate = str(get_previous_trading_day(datetime.strptime(pre_date, '%Y-%m-%d').date()))
                jinliang1 = float(getJinLiang(_preDate,buyStock["code"]))
                jinliang2 = float(getJinLiang(pre_date,buyStock["code"]))
                jinliang3 = float(getJinLiang(date,buyStock["code"]))
                #大换手并且前两日资金呈净流出,且当日资金呈现净流出则直接忽略该股
                if isHightChangeHands(pre_date,buyStock) and (jinliang2 + jinliang1 < 0) and jinliang3 < 0:
                    reason = f'1.{buyStock["name"]}股票处于高位高换手，且最近两日主力净量呈现净流出，主动空仓;\n'
                    print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
                    print(Style.RESET_ALL)
                    dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
                    stockPool = [] 
                else:
                    if buyStock['next_isLimitUp'] and not forecast:
                        for stock in todayStocks:
                            if buyStock['code'] == stock['code']:
                               first_limit_time = stock['first_limit_time']
                               break
                    #获取当日竞价信息,当日竞价幅度必须高于昨日否则空仓
                    pre_opening_increase = float(buyStock['opening_increase'].strip('%'))
                    # 检测是否都是开盘就处于涨停价位
                    if pre_opening_increase >= 9.5 and next_opening_increase >= 9.5 and abs(pre_opening_increase - next_opening_increase) <= 0.5:
                        bothIsLimitPrice = True
                    else:
                        bothIsLimitPrice = False
                    #如果昨日出现最大换手且烂板则主动空仓
                    # print(f'😁-->>{pre_opening_increase}->>{next_opening_increase}-->>{bothIsLimitPrice}-->>{len(targetStocks)}-->{date}->>{buyStock["name"]}')
                    if (pre_opening_increase < next_opening_increase or bothIsLimitPrice) or len(targetStocks) > 1 and next_opening_increase > 0:
                        if (pre_opening_increase <= next_opening_increase or bothIsLimitPrice) and len(limit_no_buy_stocks) > 0:
                            print(Fore.RED + f'{Fore.GREEN}----->>>{Fore.RED}准备涨停打板买入{buyStock["name"]}{Fore.GREEN}<<<-----\n{Fore.RED}原因:\n1.今日竞价涨幅大于或约等于昨日，接力情绪增强;\n2.有一字板做助攻;\n')
                        elif (pre_opening_increase <= next_opening_increase or bothIsLimitPrice):
                            print(Fore.RED + f'{Fore.GREEN}----->>>{Fore.RED}准备涨停打板买入{buyStock["name"]}{Fore.GREEN}<<<-----\n{Fore.RED}原因:\n1.今日竞价涨幅大于或约等于昨日，接力情绪增强;\n')
                        elif(len(limit_no_buy_stocks) > 0):
                            print(Fore.RED + f'{Fore.GREEN}----->>>{Fore.RED}准备涨停打板买入{buyStock["name"]}{Fore.GREEN}<<<-----\n{Fore.RED}原因:\n1.有一字板做助攻且开盘竞价涨幅大于0%;\n')
                        else:
                            print(Fore.RED + f'{Fore.GREEN}----->>>{Fore.RED}准备涨停打板买入{buyStock["name"]}{Fore.GREEN}<<<-----\n{Fore.RED}原因:\n1.虽然涨幅涨幅有所衰减，但是依然是竞争者中最强;\n')
                        print(Style.RESET_ALL)
                        # print(f'😁-->>{buyStock["limit_type"]}')
                        #如果买入当日炸板,并且不能开盘就涨停,策略拒绝顶一字,且必须在早上收盘前有上板动作
                        if not forecast:
                            if  buyStock['next_isBurst'] and buyStock['next_burst_time'] !='09:30:00' and isEarly(buyStock['next_burst_time'],'11:30:00'):
                                increase = float(buyStock['next_close_increase'].strip('%'))
                                earnings = increase-10
                                #精确到小数点后面两位
                                earnings = formartNumber(earnings)
                                final_money = latestMoney + latestMoney * current_shipping_space * earnings/100
                                updateStock = getTodayStock(todayStocks,buyStock)
                                if (pre_opening_increase <= next_opening_increase or bothIsLimitPrice) and len(limit_no_buy_stocks) > 0:
                                    reason = f'1.{buyStock["name"]}今日竞价涨幅大于或约等于昨日，接力情绪增强;\n2.有一字板做助攻;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                elif (pre_opening_increase <= next_opening_increase or bothIsLimitPrice) and len(limit_no_buy_stocks) == 0:
                                    reason = f'1.{buyStock["name"]}今日竞价涨幅大于或约等于昨日，接力情绪增强;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                elif(len(limit_no_buy_stocks) > 0):
                                    reason = '1.有一字板做助攻且开盘竞价涨幅大于0%;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                else:
                                    reason = f'1.{buyStock["name"]}虽然涨幅涨幅有所衰减，但是依然是竞争者中最强;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                print(Style.RESET_ALL)
                                dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':f'{earnings}%','desc':f'涨停打板买入{ buyStock["name"]},结果炸板了,当日盈利{earnings}%','stock':updateStock,'suggest_shipping_space':current_shipping_space,'reason':reason})
                                stockPool.append(updateStock)
                            # 如果涨停且不是一字涨停
                            elif buyStock['next_isLimitUp'] and not buyStock['next_isLimitUpNoBuy']:
                                updateStock = getTodayStock(todayStocks,buyStock)
                                if (pre_opening_increase <= next_opening_increase or bothIsLimitPrice) and len(limit_no_buy_stocks) > 0:
                                    reason = f'1.{buyStock["name"]}今日竞价涨幅大于或约等于昨日，接力情绪增强;\n2.有一字板做助攻;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                elif (pre_opening_increase <= next_opening_increase or bothIsLimitPrice) and len(limit_no_buy_stocks) == 0:
                                    reason = f'1.{buyStock["name"]}今日竞价涨幅大于或约等于昨日，接力情绪增强;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                elif(len(limit_no_buy_stocks) > 0):
                                    reason = '1.有一字板做助攻且开盘竞价涨幅大于0%;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                else:
                                    reason = f'1.{buyStock["name"]}虽然涨幅涨幅有所衰减，但是依然是竞争者中最强;\n'
                                    print(Fore.RED + f'涨停打板买入{buyStock["name"]}\n原因:\n{reason}')
                                print(Style.RESET_ALL)
                                dragon_log_data.append({'date':date, 'money':round(latestMoney), 'earnings':'0%','desc':f'涨停打板买入{buyStock["name"]}','stock':updateStock,'suggest_shipping_space':current_shipping_space,'reason':reason})
                                stockPool.append(updateStock)
                            #如果开盘就一字涨停则主动空仓
                            elif buyStock['next_burst_time'] =='09:30:00' or buyStock['next_isLimitUpNoBuy']:
                                reason = f'1.{buyStock["name"]}开盘一字涨停，主动空仓;\n'
                                print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
                                print(Style.RESET_ALL)
                                dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
                            #没有上板动作
                            else:
                                reason = f'1.{buyStock["name"]}在上午的交易时间段内没有触摸涨停;\n'
                                print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
                                print(Style.RESET_ALL)
                                dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
                                stockPool = []
                    else:
                        reason = f'1.{buyStock["name"]}今日竞价涨幅小于昨日，接力情绪减弱;\n2.没有一字板做助攻;\n'
                        print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
                        print(Style.RESET_ALL)
                        dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
                        stockPool = []
            elif len(limit_no_buy_stocks) > 0 and len(max_increase_stock) == 0:
                # 空仓
                reason = '1.目标个股一字板没有买入机会;'
                print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
                print(Style.RESET_ALL)
                dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
                stockPool = []
            else:
                # 空仓
                reason = '1.目标个股在上午的交易时间段内没有触摸涨停;'
                print(Fore.YELLOW + f'空仓\n原因:\n{reason}')
                print(Style.RESET_ALL)
                dragon_log_data.append({'date':date, 'money':latestMoney, 'earnings':'0%','desc':'空仓','suggest_shipping_space':current_shipping_space,'reason':reason})
                stockPool = []
    #卖出股票
    else:
        buyStock = stockPool[0]
        #获取当日竞价信息
        opening_increase = getOpeningIncrease(browserTab,date,buyStock['code'])
        next_opening_increase = float(opening_increase[0].strip('%'))
        #纠正错误的数据
        if next_opening_increase == -313:
           next_opening_increase = -3.13
        #如果昨日未出现炸板今日竞价低于0%则直接卖出
        if buyStock['isBurst'] and next_opening_increase < -3 or next_opening_increase < 0 and int(buyStock['limit_open_times'])  == 0 or next_opening_increase < -3 and int(buyStock['limit_open_times'])  > 0:
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
            reason = '触发下面三个条件其中一个\n1.个股炸板且当日开盘涨幅小于-3%;\n2.个股买入后未曾开板，但是开盘竞价为负;\n3.买入后曾经开板，但是当日竞价涨幅小于-3%;\n'
            print(Fore.GREEN + f'😁竞价卖出{buyStock["name"]}\n原因:{reason}')
            if forecast:
               print(Fore.YELLOW + f'😁卖出策略:观察开盘后的分时走势，如果快速向下则直接摁掉，如果开盘向上则可以多拿一会儿')
            print(Style.RESET_ALL)
            dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':f'{next_opening_increase}%','desc':f'竞价卖出{buyStock["name"]},当日盈利{next_opening_increase}%','suggest_shipping_space':next_shipping_space,'reason':reason})
        elif not forecast:
            burstData = judgeBurst(browserTab,date,buyStock['code'])
            isLimit = buyStock['next_isLimitUp']
            #如果炸板则卖出
            if burstData[0]:
               stockPool = []
               final_money = latestMoney + latestMoney * current_shipping_space * 10/100
               reason = '1.炸板卖出;\n'
               print(Fore.GREEN + f'炸板卖出{buyStock["name"]}\n原因:\n{reason}')
               print(Style.RESET_ALL)
               dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':'10%','desc':f'炸板卖出{buyStock["name"]},当日盈利10%','suggest_shipping_space':1,'reason':reason})
            #如果没有炸板并且继续涨停则持有
            elif isLimit:
                updateStock = getTodayStock(todayStocks,buyStock)
                final_money = latestMoney + latestMoney * current_shipping_space * 10/100
                reason = '1.继续涨停;\n'
                print(Fore.RED + f'继续持有{buyStock["name"]}\n原因:\n{reason}')
                print(Style.RESET_ALL)
                stockPool = [updateStock]
                dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':'10%','desc':f'继续持有{buyStock["name"]},当日盈利10%','stock':updateStock,'suggest_shipping_space':current_shipping_space,'reason':reason})
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
               reason = '1.未能继续涨停;\n'
               print(Fore.GREEN + f'断板卖出{buyStock["name"]}\n原因:\n{reason}')
               print(Style.RESET_ALL)
               dragon_log_data.append({'date':date, 'money':round(final_money), 'earnings':f'{earnings}%','desc':f'断板卖出{buyStock["name"]},当日盈利{earnings}%','suggest_shipping_space':next_shipping_space,'reason':reason})
        elif forecast:
             print(Fore.YELLOW + f'😁竞价符合预期注意观察分时走势')   
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stock_log_data.json', 'w') as file:
        json.dump(dragon_log_data, file,ensure_ascii=False,  indent=4) 

# # 获取下一个交易日
# date_object = datetime.strptime(dates[0], '%Y-%m-%d').date()
# next_date = calendar.valid_days(start_date=date_object + timedelta(days=1), end_date='2100-01-01')[0]
# today = datetime.now().date()
# findIndex = 1

# for index,item in enumerate(dates):
#     if '2024-04-01' == item:
#        findIndex = index 
#        break
if forecast:
#    strategy(str(date_object),str(today))
   strategy('2024-06-24','2024-06-25')
else:
    for idx, date in enumerate(dates[1:]):
        strategy(str(get_previous_trading_day(datetime.strptime(date, '%Y-%m-%d').date())),date)
   