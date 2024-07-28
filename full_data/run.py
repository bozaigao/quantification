import subprocess
import time

# Python脚本路径
script_path = "/Users/yanbo.he/Desktop/AI/quantification/full_data/dragon_strategy.py"

while True:
    try:
        result = subprocess.run(['python3', script_path], check=True)
        if result.returncode == 0:
            print("Python script executed successfully.")
            break
    except subprocess.CalledProcessError:
        print("Python script failed. Retrying...")
        time.sleep(1)  # 等待1秒后重试
