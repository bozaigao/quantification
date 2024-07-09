# increase.py
from bs4 import BeautifulSoup
import re
global_wait_seconds = 3
def getOpeningIncrease(browserTab, date, code):
    browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={date} '{code}'竞价涨幅&querytype=stock")
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    div_text = soup.find('div', class_='jgy_txt_isLayout').get_text(strip=True)
    paragraphs = soup.find_all('p', recursive=False)
    match = re.search(r'竞价涨幅(-?\d+\.\d+%)', div_text)
    if not match:
        match = re.search(r'竞价涨幅为(-?\d+\.\d+%)', div_text)
    if match:
        percentage_text = match.group(1)
    else:
        percentage_text = '0%'
    return [percentage_text,div_text]
