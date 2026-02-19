import psutil
import requests
import time
import socket

SERVER_URL = "http://localhost:5000/report"

# 이전 네트워크 데이터 저장용 (속도 계산)
last_net_io = psutil.net_io_counters()
last_time = time.time()

def get_pc_stats():
    global last_net_io, last_time
    
    # 1. CPU & RAM & Hostname
    stats = {
        "hostname": socket.gethostname(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_usage": psutil.virtual_memory().percent,
    }

    # 2. Disk C & D (상세 용량 포함)
    for drive in ['C', 'D']:
        try:
            usage = psutil.disk_usage(f'{drive}:/')
            stats[f"disk_{drive.lower()}"] = usage.percent
            stats[f"disk_{drive.lower()}_total"] = round(usage.total / (1024**3), 1)
            stats[f"disk_{drive.lower()}_free"] = round(usage.free / (1024**3), 1)
        except:
            stats[f"disk_{drive.lower()}"] = None if drive == 'D' else 0
            stats[f"disk_{drive.lower()}_total"] = 0
            stats[f"disk_{drive.lower()}_free"] = 0

    # 3. 네트워크 속도 계산 (MB/s)
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    interval = current_time - last_time
    
    stats["net_sent"] = round((current_net_io.bytes_sent - last_net_io.bytes_sent) / (1024**2) / interval, 2)
    stats["net_recv"] = round((current_net_io.bytes_recv - last_net_io.bytes_recv) / (1024**2) / interval, 2)
    
    last_net_io = current_net_io
    last_time = current_time

    # 4. CPU 점유율 Top 3 프로세스
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # CPU 사용량 순으로 정렬 후 상위 3개 추출
    top_procs = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:3]
    stats["top_processes"] = [f"{p['name']}({p['cpu_percent']}%)" for p in top_procs]

    return stats

def start_monitoring():
    print("Monitoring started with Network & Top Processes...")
    while True:
        try:
            stats = get_pc_stats()
            requests.post(SERVER_URL, json=stats, timeout=5)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(4) # 데이터 수집 간격

if __name__ == "__main__":
    start_monitoring()