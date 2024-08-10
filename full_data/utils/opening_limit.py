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
def judgeOpeningLimit(browserTab, date, code):
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
      table_with_attribute = soup.find('table', {'data-v-00e1661f': True})
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
