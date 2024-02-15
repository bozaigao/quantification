# limitUtil.py
from bs4 import BeautifulSoup
global_wait_seconds = 3
def getLimitUPs(browserTab, date):
    browserTab.Page.navigate(url="https://www.iwencai.com/unifiedwap/result?w=" + date + "主板非st涨停&querytype=stock")
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    target_span = soup.find('span', class_='ui-f24 ui-fb red_text ui-pl8')
    if target_span:
       limit_ups = target_span.get_text(strip=True)
       print('涨停'+limit_ups)
       return limit_ups
    else:
        return 0

def getLimitDowns(browserTab, date):
    browserTab.Page.navigate(url="https://www.iwencai.com/unifiedwap/result?w=" + date + "主板非st跌停&querytype=stock")
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    target_span = soup.find('span', class_='ui-f24 ui-fb red_text ui-pl8')
    if target_span:
       limit_downs = target_span.get_text(strip=True)
       print('跌停'+limit_downs)
       return limit_downs
    else:
        return 0
