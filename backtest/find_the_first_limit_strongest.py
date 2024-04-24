#找出指定日期资金流入最强个股
import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
from  utils.judgeBurst import judgeBurst
import pychrome
import math
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup

global_wait_seconds = 3
# 指定回测年份
year = 2024
#交易日期
dates = []
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()
strongest_pool = []
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []
find_date = datetime.strptime('2024-02-23', '%Y-%m-%d').date()
browserTab.Page.navigate(url="https://www.iwencai.com/unifiedwap/result?w=" + str(find_date) + "主板非st涨停且按最终涨停时间排序&querytype=stock")
browserTab.wait(global_wait_seconds)
result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
soup = BeautifulSoup(result['result']['value'], 'html.parser')
# 获取 tbody 中所有的 tr 标签
tbodies = soup.find_all('tbody', {'data-v-00e1661f': True})
tbody = tbodies[0]
if tbody:
    tr_tags = tbody.find_all('tr')
    stocks = []
    # 获取涨停信息
    for tr in tr_tags:
        td_tags = tr.find_all('td')
        if len(td_tags) >= 22:
            #代码
            code_td = td_tags[2] 
            if code_td:
                code = code_td.text.strip() 
            #名字
            name_td = td_tags[3]
            if name_td:
                a_tag = name_td.find('a')
                if a_tag:
                        company_name = a_tag.text
            #价格
            price_td = td_tags[4]
            if price_td:
                price = price_td.text.strip()
            #首次涨停时间
            first_limit_time_td = td_tags[6]
            if first_limit_time_td:
                first_limit_time = first_limit_time_td.text.strip()
            #连板数
            limit_td = td_tags[7]
            if limit_td:
               limit = limit_td.text.strip()
            #最终涨停时间
            final_limit_time_td = td_tags[8]
            if final_limit_time_td:
                final_limit_time = final_limit_time_td.text.strip()
            #涨停概念
            limit_reason_td = td_tags[10]
            if limit_reason_td:
                a_tag = limit_reason_td.find('a')
                if a_tag:
                        limit_reason = a_tag.text
            #涨停封单量
            limit_tocks_td = td_tags[11]
            if limit_tocks_td:
                limit_tocks = limit_tocks_td.text.strip()
            #涨停封单金额
            limit_money_td = td_tags[12]
            if limit_money_td:
                limit_money = limit_money_td.text.strip()
            #涨停封成比
            limit_cheng_ratio_td = td_tags[13]
            if limit_cheng_ratio_td:
                limit_cheng_ratio = limit_cheng_ratio_td.text.strip()
            #涨停封流比
            limit_liu_ratio_td = td_tags[14]
            if limit_liu_ratio_td:
                limit_liu_ratio = limit_liu_ratio_td.text.strip()
            #涨停开板次数
            limit_open_times_td = td_tags[15]
            if limit_open_times_td:
                limit_open_times = limit_open_times_td.text.strip()
            #流通市值
            market_value_td = td_tags[16]
            if market_value_td:
                a_tag = market_value_td.find('a')
                if a_tag:
                        market_value = a_tag.text
            #涨停类型
            limit_type_td = td_tags[18]
            if limit_type_td:
                limit_type = limit_type_td.text.strip()
            #公司注册地址
            company_place_td = td_tags[20]
            if company_place_td:
                company_place = company_place_td.text.strip()
            #公司经营范围
            company_business_td = td_tags[21]
            if company_business_td:
                company_business = company_business_td.text.strip()
        stock = {'code':code,'name':company_name,'limit':int(limit),'price':price,'first_limit_time':first_limit_time,
        'final_limit_time':final_limit_time,'limit_reason':limit_reason,'limit_tocks':limit_tocks,'limit_money':limit_money,'limit_cheng_ratio':limit_cheng_ratio,'limit_liu_ratio':limit_liu_ratio,
        'limit_open_times':limit_open_times,'market_value':market_value,'limit_type':limit_type,'company_place':company_place,'company_business':company_business}
        if stock["limit"] == 1:
           stocks.append(stock)

# stocks = stocks[:5]
batch_size = 19
# 存储结果的列表
data_list = []
#获取竞价信息
for i in range(len(stocks)):
    # 计算当前批次的开始和结束索引
    start_index = i * batch_size
    end_index = start_index + batch_size
    # 获取当前批次的股票
    current_batch = stocks[start_index:end_index]
    # 初始化搜索文本
    search_text = ''
    # 拼接当前批次的股票代码
    for item in current_batch:
        search_text += f',{item["code"]}'
    # 添加 '竞价' 文字到搜索文本中
    search_text += '竞价'
    # 打印当前的搜索文本，可以选择注释掉这一行
    if search_text == '竞价':
        break
    # 导航到搜索页面
    browserTab.Page.navigate(url=f"https://www.iwencai.com/stockpick/search?rsh=3&typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={str(find_date)}{search_text}")
    # 等待页面加载
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    # 找到包含股票代码和简称的表格
    table = soup.find('table', class_='static_table tbody_table static_tbody_table')
    # 存储结果的列表
    stocks_data = []
    # 遍历表格中的每一行
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 4:  # 确保每行中有足够的单元格数据
            # 提取股票代码和简称
            stock_code = cells[2].text.strip()
            stock_name_link = cells[3].find('a')
            if stock_name_link:
                stock_name = stock_name_link.text.strip()
                stocks_data.append({
                    'stock_code': stock_code,
                    'stock_name': stock_name
                })
    table = soup.find('table', class_='scroll_table tbody_table scroll_tbody_table')
    # 遍历表格中的每一行
    for index,row in enumerate(table.find_all('tr')):
        # 按顺序获取列数据
        columns = row.find_all('td')
        if len(columns) >= 12:  # 确保每行有足够的数据列
            bidding_increase = columns[2].text.strip()  # 竞价涨幅
            bidding_volume = columns[7].text.strip()  # 竞价量
            bidding_amount = columns[8].text.strip()  # 竞价金额
            # 添加到结果列表
            data_list.append({
                'stock_code': stocks_data[index]["stock_code"],
                'stock_name': stocks_data[index]["stock_name"],
                'bidding_increase': f'{bidding_increase}%',
                'bidding_volume': bidding_volume,
                'bidding_amount': bidding_amount
            })

hot_stocks_data = []
# 获取股票热度信息
for i in range(len(data_list)):
    # 计算当前批次的开始和结束索引
    start_index = i * batch_size
    end_index = start_index + batch_size
    # 获取当前批次的股票
    current_batch = data_list[start_index:end_index]
    # 初始化搜索文本
    search_text = ''
    # 拼接当前批次的股票代码
    for item in current_batch:
        search_text += f',{item["stock_code"]}'
    # 添加 '竞价' 文字到搜索文本中
    search_text += '热度'
    # 打印当前的搜索文本，可以选择注释掉这一行
    if search_text == '热度':
        break
    # 导航到搜索页面
    browserTab.Page.navigate(url=f"https://www.iwencai.com/stockpick/search?rsh=3&typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={str(find_date)}{search_text}")
    # 等待页面加载
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    # 初始化列表来保存每只股票的代码和简称
    stock_info = []
    # 先找到具体的<table>标签
    table = soup.find('table', class_='static_table tbody_table static_tbody_table')
    # 在找到的<table>中遍历<tbody>中的<tr>标签
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 4:  # 确保<td>标签的数量足够
            stock_code = cells[2].get_text(strip=True)  # 获取股票代码
            stock_name = cells[3].text.strip()  # 获取股票简称，使用.text.strip()更清晰
            stock_info.append({
                    'stock_code': stock_code,
                    'stock_name': stock_name
                })
    # 定位到具体的<table>标签
    table = soup.find('table', class_='scroll_table tbody_table scroll_tbody_table')
    # 在找到的<table>中遍历<tbody>中的<tr>标签
    tbody = table.find('tbody')
    for index, row in enumerate(tbody.find_all('tr')):
        cells = row.find_all('td')
        if len(cells) >= 5:  # 确保列数足够
            volume = cells[2].get_text(strip=True)  # 交易量，即“热度”
            rank = cells[3].get_text(strip=True)    # 排名
            hot_stocks_data.append({"stock_code":stock_info[index]["stock_code"],"stock_name":stock_info[index]["stock_name"], "rank":rank,"volume":volume})
for item in data_list:
    for item2 in hot_stocks_data:
        if item["stock_code"] == item2["stock_code"]:
            item["rank"] = item2["rank"].replace(',', '')
            item["volume"] = item2["volume"]
data_list = sorted(data_list, key=lambda x: int(x['rank']))
# with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_test.json', 'w') as file:
#     json.dump(data_list, file,ensure_ascii=False,  indent=4) 
for item in stocks_data:
    dates.append(item['date'])
# 从指定日期开始向前搜索上一个交易日
def get_previous_trading_day(date_object):
    while True:
        date_object -= timedelta(days=1)  # 递减一天
        if str(date_object) in dates:  # 如果是交易日，则返回该日期
            return date_object
# find_date = datetime.now().date()
pre_date = get_previous_trading_day(find_date)
print(f'今日:{str(find_date)},昨日:{str(pre_date)}')
for index1, item in enumerate(stocks_data):
    if item['date'] == str(pre_date):
        for index2, item2 in enumerate(item['data']):
            if item2['limit'] > 1:
                if "current_opening_increase" in stocks_data[index1]["data"][index2]:
                    pre_opening_increase = float(stocks_data[index1]["data"][index2]["current_opening_increase"].strip('%'))
                else:
                    pre_opening_increase = float(getOpeningIncrease(browserTab,str(pre_date),item2['code'])[0].strip('%'))
                    stocks_data[index1]["data"][index2]["current_opening_increase"] = f'{pre_opening_increase}%'
                if "next_opening_increase" in stocks_data[index1]["data"][index2]:
                    current_opening_increase = float(stocks_data[index1]["data"][index2]["next_opening_increase"].strip('%'))
                else:
                    current_opening_increase = float(getOpeningIncrease(browserTab,str(find_date),item2['code'])[0].strip('%'))
                    stocks_data[index1]["data"][index2]["next_opening_increase"] = f'{current_opening_increase}%'
                with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'w') as file:
                    json.dump(stocks_data, file,ensure_ascii=False,  indent=4) 
                if pre_opening_increase >= 9.5 and current_opening_increase >= 9.5 and abs(pre_opening_increase - current_opening_increase) <= 0.5:
                    bothIsLimitPrice = True
                else:
                    bothIsLimitPrice = False
                if current_opening_increase > pre_opening_increase or bothIsLimitPrice:
                   strongest_pool.append({'date':str(find_date),'name':item2['name'],'pre_opening_increase':pre_opening_increase,'current_opening_increase':current_opening_increase,'limit':item2['limit']})

strongest_pool = sorted(strongest_pool, key=lambda x: (-x['limit'], -x['current_opening_increase']))
for index, item in enumerate(strongest_pool):
    if item["limit"] > 2:
       print(Fore.RED + f'{index+1}.{item["name"]},昨日竞价{item["pre_opening_increase"]}%,当日竞价{item["current_opening_increase"]}%,{item["limit"]}板, 振幅{round(abs(item["current_opening_increase"] - item["pre_opening_increase"]),2)}%')
    else:
       print(Fore.GREEN + f'{index+1}.{item["name"]},昨日竞价{item["pre_opening_increase"]}%,当日竞价{item["current_opening_increase"]}%,{item["limit"]}板, 振幅{round(abs(item["current_opening_increase"] - item["pre_opening_increase"]),2)}%')
