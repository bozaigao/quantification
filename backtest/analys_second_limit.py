#分析二板中都有哪些共同规律：前一日竞价涨幅、当日竞价涨幅、振幅、个股热度、个股当日竞价放量程度、首次封板时间、市值大小
import os
import re
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
strongest_pool = []
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []
for item in stocks_data:
    dates.append(item['date'])
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_second_limit.json', 'r',) as file:
        data_list = json.load(file)
except FileNotFoundError:
    data_list = []

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_second_limit_analys.json', 'r',) as file:
        second_data_list = json.load(file)
except FileNotFoundError:
    second_data_list = []
def convert_to_number(s):
    # 检查是否含有'万'，如果有，则乘以10000
    multiplier = 10000 if '万' in s else 1
    # 移除数字中的'万'和逗号
    s = re.sub('[万,]', '', s)
    # 转换为浮点数并根据是否有'万'调整数值
    return float(s) * multiplier

# 从指定日期开始向前搜索上一个交易日
def get_previous_trading_day(date_object):
    if str(date_object) == '2023-01-03':
        return '2022-12-30'
    while True:
        date_object -= timedelta(days=1)  # 递减一天
        if str(date_object) in dates:  # 如果是交易日，则返回该日期
            return date_object

def get_jingjia_info(date,stocks):
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
        if len(search_text) <= 7:
            search_text += search_text
        # 添加 '竞价' 文字到搜索文本中
        search_text += '竞价'
        # 打印当前的搜索文本，可以选择注释掉这一行
        if search_text == '竞价':
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
                stock_code = cells[2].text.strip()
                stock_name_link = cells[3].find('a')
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
            if len(columns) >= 12:  # 确保每行有足够的数据列
                bidding_increase = columns[2].text.strip()  # 竞价涨幅
                bidding_volume = columns[7].text.strip()  # 竞价量
                bidding_amount = columns[8].text.strip()  # 竞价金额
                # 添加到结果列表
                data_list.append({
                    'code': stocks_data[index]["code"],
                    'name': stocks_data[index]["name"],
                    'pre_bidding_increase': f'{bidding_increase}%',
                    'pre_bidding_volume': bidding_volume,
                    'pre_bidding_amount': bidding_amount
                })
    return data_list

if len(data_list) == 0:
    for item in stocks_data[len(second_data_list):]:
        filter_stocks = [stock for stock in item['data'] if stock['limit'] == 2]
        # 存储结果的列表
        pre_date = get_previous_trading_day(datetime.strptime(item['date'], '%Y-%m-%d').date())
        find_date = item['date']
        data_list = get_jingjia_info(pre_date,filter_stocks)
        #获取竞价信息
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
                search_text += f',{item["code"]}'
            # 添加 '竞价' 文字到搜索文本中
            search_text += '热度'
            # 打印当前的搜索文本，可以选择注释掉这一行
            if search_text == '热度':
                break
            # 导航到搜索页面
            browserTab.Page.navigate(url=f"https://www.iwencai.com/stockpick/search?rsh=3&typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={str(pre_date)}{search_text}")
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
                            'code': stock_code,
                            'name': stock_name
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
                    hot_stocks_data.append({"code":stock_info[index]["code"],"name":stock_info[index]["name"], "rank":rank,"volume":volume})
        for item in data_list:
            for item2 in hot_stocks_data:
                if item["code"] == item2["code"]:
                    item["rank"] = item2["rank"].replace(',', '')
                    item["volume"] = item2["volume"]
        for item in data_list:
            for item2 in filter_stocks:
                if item2["code"] == item["code"]:
                    item2["rank"] = item["rank"].replace(',', '')
                    item2["volume"] = item["volume"]
                    item2["pre_bidding_increase"] = item["pre_bidding_increase"]
                    item2["pre_bidding_volume"] = item["pre_bidding_volume"]
                    item2["pre_bidding_amount"] = item["pre_bidding_amount"]
        next_data_list = get_jingjia_info(find_date, data_list)
        for item in next_data_list:
            for item2 in filter_stocks:
                if item2["code"] == item["code"]:
                    item2["bidding_increase"] = item["pre_bidding_increase"]
                    item2["bidding_volume"] = item["pre_bidding_volume"]
                    item2["bidding_amount"] = item["pre_bidding_amount"]
        second_data_list.append({'date':find_date,'data':filter_stocks})
        with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_second_limit_analys.json', 'w') as file:
                json.dump(second_data_list, file,ensure_ascii=False,  indent=4) 