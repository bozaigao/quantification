import json

# 打开 package-lock.json 文件
with open('package-lock.json', 'r') as f:
    data = json.load(f)

# 函数递归搜索所有 "node" engines 信息
def find_engines(data, engines):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'engines' and 'node' in value:
                engines.add(value['node'])
            else:
                find_engines(value, engines)
    elif isinstance(data, list):
        for item in data:
            find_engines(item, engines)

engines = set()
find_engines(data, engines)

# 输出所有发现的 Node.js 版本要求
print("Found Node.js version requirements in package-lock.json:")
for engine in engines:
    print(engine)
