import subprocess
import time

# Python脚本路径
script_path = "/Users/yanbo.he/Desktop/AI/quantification/full_data/dragon_strategy.py"
max_retries = 10
retry_count = 0
while True:
    try:
        result = subprocess.run(['python3', script_path], check=True)
        if result.returncode == 0:
            print("Python script executed successfully.")
            break
    except subprocess.CalledProcessError:
        retry_count += 1
        if retry_count > max_retries:
            print("Python script failed after 5 retries. Terminating script.")
            break
        print(f"Python script failed. Retrying... ({retry_count}/{max_retries})")
        time.sleep(1)
