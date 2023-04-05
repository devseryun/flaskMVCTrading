# run_both.py
import subprocess

# Windows 사용자인 경우 'python' 대신 'python3'를 사용하십시오.
app_process = subprocess.Popen(["python3", "app.py"])
stock_process = subprocess.Popen(["python3", "stock_program.py"])

app_process.wait()
stock_process.wait()
