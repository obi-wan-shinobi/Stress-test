from multiprocessing import Process, active_children, cpu_count, Pipe
import os
import signal
import sys
import time
import psutil

DEFAULT_TIME = 60
TOTAL_CPU = cpu_count()
DEFAULT_MEMORY = psutil.virtual_memory().total >> 20
PERCENT = 100
OFFSET = 0
GIGA = 2 ** 30
MEGA = 2 ** 20

def loop(conn):
    global PERCENT, OFFSET
    proc_info = os.getpid()
    conn.send(proc_info)
    conn.close()
    while True:
        if(psutil.cpu_percent() > PERCENT):
            #time.sleep(5)
            continue
        1*1

def sigint_handler(signum, frame):
    procs = active_children()
    for p in procs:
        p.terminate()
    os._exit(1)

signal.signal(signal.SIGINT, sigint_handler)

def get_args():
    exec_time = DEFAULT_TIME
    proc_num = TOTAL_CPU
    percent = 100
    memory = DEFAULT_MEMORY
    if(len(sys.argv) > 4):
        raise
    if(len(sys.argv) == 2):
        percent = int(sys.argv[1])
        proc_num = (percent * TOTAL_CPU)//100
    if(len(sys.argv) == 3):
        percent = int(sys.argv[1])
        proc_num = (percent * TOTAL_CPU)//100
        exec_time = int(sys.argv[2])
    if(len(sys.argv) == 4):
        percent = int(sys.argv[1])
        proc_num = (percent * TOTAL_CPU)//100
        exec_time = int(sys.argv[2])
        memory = int(sys.argv[3])

    return exec_time, proc_num, percent, memory

def pmem():
    tot, avail, percent, used, free = psutil.virtual_memory()
    tot, avail, used, free = tot / GIGA, avail / GIGA, used / GIGA, free / GIGA
    print("---------------------------------------")
    print("Memory Stats: total = %s GB \navail = %s GB \nused = %s GB \nfree = %s GB \npercent = %s"
          % (tot, avail, used, free, percent))

def alloc_max_str(memory, exec_time):
    i = 0
    a = ''
    while True:
        try:
            a = ' ' * (i * 1024 * MEGA)
            if((psutil.virtual_memory().used >> 20) > memory):
                #time.sleep(exec_time)
                break
            del a
        except MemoryError:
            break
        i += 1
    return a

def memory_stress(memory, exec_time):
    pmem()
    a = alloc_max_str(memory, exec_time)
    pmem()
    print("Memory Filled:")
    print("Waiting for %d sec"%(exec_time))
    return a;

def cpu_stress():
    try:
        exec_time, proc_num, cpu_percent, memory = get_args()
        global PERCENT
        PERCENT = cpu_percent
    except:
        msg = "Usage: stress_test [CPU percent] [exec_time] [Memory in MB]"
        sys.stderr.write(msg)
        sys.exit(1)
    procs = []
    conns = []
    print("CPU and Memory Stress in progress:")
    a = memory_stress(memory, exec_time)

    for i in range(proc_num+1):
        parent_conn, child_conn = Pipe()
        p = Process(target=loop, args=(child_conn,))
        p.start()
        procs.append(p)
        conns.append(parent_conn)

    for conn in conns:
        try:
            print(conn.recv())
        except EOFError:
            continue

    time.sleep(exec_time)

    del a

    for p in procs:
        p.terminate()

if __name__ == "__main__":
    cpu_stress()
