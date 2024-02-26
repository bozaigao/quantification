import shutil
import sys
import os

class AnalyzeExit(Exception):
    pass

current_directory = os.getcwd()
# backtest 目录路径
backtest_directory = os.path.join(current_directory, "backtest")
sys.path.append(backtest_directory)


try:
    exec(open("analyze.py").read())
except AnalyzeExit:
    print("Analyze.py terminated early; continuing with the next script.")
    
exec(open("opening_increase.py").read())
exec(open("canvas.py").read())

# 拷贝文件到备份目录
shutil.copy('2024年A股主板连板数据.xlsx', os.path.join('2024', '2024年A股主板连板数据.xlsx'))
shutil.copy('2024_stocks_data.json', os.path.join('2024', '2024_stocks_data.json'))
shutil.copy('2024_dragon_opening_data.json', os.path.join('2024', '2024_dragon_opening_data.json'))
shutil.copy('2024_dragon_data.json', os.path.join('2024', '2024_dragon_data.json'))

# 拷贝文件到backtest数据回测目录
shutil.copy('2024_dragon_opening_data.json', os.path.join('backtest', '2024_dragon_opening_data.json'))
os.chdir(backtest_directory)
exec(open(os.path.join(backtest_directory, "computing_data.py")).read())
exec(open(os.path.join(backtest_directory, "dragon_strategy.py")).read())
os.chdir(current_directory)
shutil.copy(os.path.join('backtest', '2024_dragon_backtest_data.json'), os.path.join('2024', '2024_dragon_backtest_data.json'))