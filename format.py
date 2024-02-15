import json
source_file_path = '2024_stocks_data.json'
output_file_path = '2024_stocks_data.json'

# 打开源文件，读取内容（这里假设源文件编码为'GBK'，根据实际情况调整）
with open(source_file_path, 'r', encoding='GBK') as file:
    content = json.load(file)

# 将读取的内容以UTF-8编码写入新文件
with open(output_file_path, 'w', encoding='utf-8') as output_file:
     json.dump(content, output_file,ensure_ascii=False,  indent=4) 

print('文件内容已转换为UTF-8编码并保存到新文件。')
