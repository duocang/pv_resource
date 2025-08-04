import psutil
import time

# 获取每个 CPU 核心的使用率（间隔1秒）
cpu_percent_per_core = psutil.cpu_percent(percpu=True, interval=1)

for i, percent in enumerate(cpu_percent_per_core):
    print(f"CPU Core {i}: {percent}%")