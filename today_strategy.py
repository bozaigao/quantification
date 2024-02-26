import shutil
import sys
import os

current_directory = os.getcwd()
# backtest 目录路径
backtest_directory = os.path.join(current_directory, "backtest")
sys.path.append(backtest_directory)
os.chdir(backtest_directory)
exec(open(os.path.join(backtest_directory, "dragon_strategy.py")).read())