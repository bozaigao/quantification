#找出指定日期资金流入最强个股
import os
import re
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from  utils.judgeBurst import judgeBurst
import pychrome
import math
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup

global_wait_seconds = 3
# 指定回测年份
year = 2024
batch_size = 17
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
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []
for item in stocks_data:
    dates.append(item['date'])
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_first_limit_backtest_data.json', 'r',) as file:
        first_limit_backtest_data = json.load(file)
except FileNotFoundError:
    first_limit_backtest_data = []
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_new_stocks_first_limit_backtest_data.json', 'r',) as file:
        new_first_limit_backtest_data = json.load(file)
except FileNotFoundError:
    new_first_limit_backtest_data = []

def get_previous_trading_day(date_object):
    if str(date_object) == '2023-01-03':
        return '2022-12-30'
    while True:
        date_object -= timedelta(days=1)  # 递减一天
        if str(date_object) in dates:  # 如果是交易日，则返回该日期
            return date_object

def getFirstLimitTime(date,code):
    browserTab.Page.navigate(url=f"https://www.iwencai.com/stockpick/search?rsh=3&typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={date} {code}涨停时间")
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    div_content = soup.find_all('div', class_=['em', '_x_', 'alignRight'])
    # 检查是否找到元素，并提取文本
    stock = {}
    for div in div_content:
        text = div.text.strip()
        if '最终涨停时间' in text:
            # 找到包含“最终涨停时间”的<div>后，下一个<div>通常包含时间
            final_stop_time_index = div_content.index(div) + 1
            final_stop_time = div_content[final_stop_time_index].text.strip()
            stock['pre_final_limit_time'] = final_stop_time
        elif '涨停开板次数' in text:
            # 找到包含“涨停开板次数”的<div>后，下一个<div>通常包含次数
            number_of_openings_index = div_content.index(div) + 1
            number_of_openings = div_content[number_of_openings_index].text.strip()
            stock['pre_open_times'] = number_of_openings
    return stock

def get_first_limit_time_info(date,stocks):
    global batch_size
    data_list = []
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
        if len(current_batch) == 1:
            stock = getFirstLimitTime(date,current_batch[0]["code"])
            data_list.append({
                    'code': current_batch[0]["code"],
                    'name': current_batch[0]["name"],
                    'pre_final_limit_time': stock['pre_final_limit_time'],
                    'pre_open_times': stock['pre_open_times']
                })
        else:
                
            # 添加 '涨停时间' 文字到搜索文本中
            search_text += '涨停时间'
            # 打印当前的搜索文本，可以选择注释掉这一行
            if search_text == '涨停时间':
                break
            # 导航到搜索页面
            browserTab.Page.navigate(url=f"https://www.iwencai.com/stockpick/search?rsh=3&typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={str(date)}{search_text}")
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
                    stock_code = cells[1].find('div', class_='em').text.strip()
                    stock_name_link = cells[2].find('a')
                    if stock_name_link:
                        stock_name = stock_name_link.text.strip()
                        stocks_data.append({
                            'code': stock_code,
                            'name': stock_name
                        })
            table = soup.find('table', class_='scroll_table tbody_table scroll_tbody_table')
            # 遍历表格中的每一行
            for index,row in enumerate(table.find_all('tr')):
                # 按顺序获取列数据
                columns = row.find_all('td')
                if len(columns) >= 10:  # 确保每行有足够的数据列
                    final_limit_time = columns[3].find('div', class_='em').text.strip()  # 最终涨停时间
                    open_times = columns[7].find('div', class_='em').text.strip()  # 开板次数
                    # 添加到结果列表
                    data_list.append({
                        'code': stocks_data[index]["code"],
                        'name': stocks_data[index]["name"],
                        'pre_final_limit_time': final_limit_time,
                        'pre_open_times': open_times
                    })
    return data_list
for item in first_limit_backtest_data[len(new_first_limit_backtest_data):]:
    data = []
    searchData = []
    for item2 in item['data']:
        data.append(item2)
        if 'isBurst' in item2:
            searchData.append(item2)
    data_list = get_first_limit_time_info(str(get_previous_trading_day(datetime.strptime(item['date'], '%Y-%m-%d').date())),searchData)
    for item3 in data_list:
        for item4 in data:
            if item3['code'] == item4['code']:
               item4['pre_final_limit_time'] = item3['pre_final_limit_time']
               item4['pre_open_times'] = item3['pre_open_times']
    new_first_limit_backtest_data.append({'date':item['date'], 'data':data})
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_new_stocks_first_limit_backtest_data.json', 'w') as file:
        json.dump(new_first_limit_backtest_data, file,ensure_ascii=False,  indent=4) 