# judgeBurst.py
from bs4 import BeautifulSoup
global_wait_seconds = 3
def judgeBurst(browserTab, date, code):
    browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={date} 主板非st炸板&querytype=stock")
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
            for row in rows:
                cells = row.find_all('td')
                arr = [cell.get_text(strip=True) for cell in cells]
                if arr[2] == code:
                       return [True,arr[6]]
        else:
            print("未找到tbody元素")
    else:
        print("未找到具有data-v-00e1661f属性的table元素")

    return [False,'']
   
