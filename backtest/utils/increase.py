# increase.py
from bs4 import BeautifulSoup
global_wait_seconds = 3

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def getIncrease(browserTab, date, name):
    resArr = []
    browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={date} {name}涨幅&querytype=stock")
    browserTab.wait(global_wait_seconds)
    result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
    soup = BeautifulSoup(result['result']['value'], 'html.parser')
    table = soup.find('table', class_='left-table')
    if table:
        second_tr = table.find_all('tr')[1]
        if second_tr:
            value_span = second_tr.find('span')
            if value_span:
                value = value_span.text.strip()
                resArr.append(value)
    # 找到表格
    table = soup.find('table', class_='right-table')
    if table:
        # 找到所有的 <tr> 元素，从第二个 <tr> 开始
        rows = table.find_all('tr')[1:]
        for row in rows:
            # 找到 <td> 元素
            cells = row.find_all('td')
            # 提取 <td> 中的文本值
            values = [cell.text.strip() for cell in cells]
            resArr.extend(values)
            if is_float(resArr[-2]):
                return resArr
            else:
                # 和最后一个元素互换位置
                resArr[-1], resArr[-2] = resArr[-2], resArr[-1]
                return resArr
