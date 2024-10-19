import json
from bs4 import BeautifulSoup
global_wait_seconds = 3
year = 2024
try:
    with open(f'./full_data/utils/{year}_stock_burst_data.json', 'r',) as file:
        stock_burst_data = json.load(file)
except FileNotFoundError:
    stock_burst_data = []

try:
    with open(f'./full_data/utils/{year}_stocks_data.json', 'r',) as file:
        stock_limit_data = json.load(file)
except FileNotFoundError:
    stock_limit_data = []
#判断是否开盘就涨停
def judgeLimit(browserTab, date, code):
    hasRecordBurst = False
    for item in stock_burst_data:
        if item['date'] == date:
            hasRecordBurst = True
            for stock in item['data']:
               if stock['code'] == code and stock['burstTime'] == '09:30:00':
                  return True
    if not hasRecordBurst:
      #从炸板中提取数据
      browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={date} 主板炸板&querytype=stock")
      browserTab.wait(global_wait_seconds)
      result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
      soup = BeautifulSoup(result['result']['value'], 'html.parser')
      # 选择符合条件的table
      table_with_attribute = soup.find('table', {'data-v-41d36628': True})
      # 如果找到table，则选择其下的tbody
      if table_with_attribute:
         tbody = table_with_attribute.find('tbody')
         # 如果找到tbody，则选择其中的所有tr
         if tbody:
               rows = tbody.find_all('tr')
               data = []
               isYiZi = False
               for row in rows:
                  cells = row.find_all('td')
                  arr = [cell.get_text(strip=True) for cell in cells]
                  data.append({"code": arr[2],"name": arr[3], "burstTime": arr[6]})
                  if arr[2] == code and arr[6] == '09:30:00':
                     isYiZi = True
               stock_burst_data.append({"date": date,"data": data})
               with open(f'./full_data/utils/{year}_stock_burst_data.json', 'w') as file:
                     json.dump(stock_burst_data, file,ensure_ascii=False,  indent=4) 
               if isYiZi:
                  return True
         else:
               print("未找到tbody元素")
      else:
         print("未找到具有data-v-00e1661f属性的table元素")

    for item in stock_limit_data:
        if item['date'] == date:
            for stock in item['data']:
                if stock['code'] == code and stock['first_limit_time'] == '09:30:00':
                    return True
                
    return False


def judgeOpeningLimit(browserTab, date, code, forecast):
    if not forecast:
        return judgeLimit(browserTab, date, code)
    else:
        limitArr = []
        if code in limitArr:
            return True
         #从涨停连板中提取数据  
        browserTab.Page.navigate(url="https://www.iwencai.com/unifiedwap/result?w=" + date + "主板涨停&querytype=stock")
        browserTab.wait(global_wait_seconds)
        result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
        soup = BeautifulSoup(result['result']['value'], 'html.parser')
        # 获取 tbody 中所有的 tr 标签
        tbodies = soup.find_all('tbody', {'data-v-41d36628': True})
        tbody = tbodies[0]
        if tbody:
            tr_tags = tbody.find_all('tr')
        stocks = []
        # 遍历所有的 tr 标签，并输出其内容
        for tr in tr_tags:
            td_tags = tr.find_all('td')
            if len(td_tags) >= 22:
            #代码
                code_td = td_tags[2] 
            if code_td:
                _code = code_td.text.strip() 
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
            if code == _code and first_limit_time == '09:30:00':
                return True
    return False