import psutil, time

while True:
    print(psutil.cpu_percent(percpu=True))
    time.sleep(1)
