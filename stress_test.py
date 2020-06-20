from multiprocessing import Process, active_children, cpu_count, Pipe
import os
import signal
import sys
import time
import psutil

DEFAULT_TIME = 60
TOTAL_CPU = psutil.cpu_count(logical=True)
DEFAULT_MEMORY = psutil.virtual_memory().total >> 20
PERCENT = 100
OFFSET = 0
GIGA = 2 ** 30
MEGA = 2 ** 20

def loop(conn, affinity):
    proc = psutil.Process()
    proc_info = proc.pid
    msg = "Process ID: "+str(proc_info)+" CPU: "+str(affinity[0])
    conn.send(msg)
    conn.close()
    proc.cpu_affinity(affinity)
    while True:
        1*1

def last_core_loop(conn, affinity, percent):
    proc = psutil.Process()
    proc_info = proc.pid
    msg = "Process ID: "+str(proc_info)+" CPU: "+str(affinity[0])
    conn.send(msg)
    conn.close()
    proc.cpu_affinity(affinity)
    while True:
        if(psutil.cpu_percent(percpu=True)[affinity[0]] > percent):
            time.sleep(0.2)
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
        if(percent > 100):
            raise
        proc_num = (percent * TOTAL_CPU)/100
    if(len(sys.argv) == 3):
        percent = int(sys.argv[1])
        if(percent > 100):
            raise
        proc_num = (percent * TOTAL_CPU)/100
        exec_time = int(sys.argv[2])
    if(len(sys.argv) == 4):
        percent = int(sys.argv[1])
        proc_num = (percent * TOTAL_CPU)/100
        exec_time = int(sys.argv[2])
        memory = int(sys.argv[3])
        if(percent > 100 or memory > DEFAULT_MEMORY):
            raise

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
            a = ' ' * (i * 256 * MEGA)
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
        constraints = "\nCPU < 100 and memory < "+str(DEFAULT_MEMORY)
        sys.stderr.write(constraints)
        sys.exit(1)
    procs = []
    conns = []
    print("CPU and Memory Stress in progress:")
    a = memory_stress(memory, exec_time)

    actual_cores = int(proc_num)
    last_core_usage = round((proc_num-actual_cores),2)*100
    proc_num = actual_cores
    for i in range(proc_num):
        parent_conn, child_conn = Pipe()
        p = Process(target=loop, args=(child_conn,[i]))
        p.start()
        procs.append(p)
        conns.append(parent_conn)

    last_core = proc_num
    parent_conn, child_conn = Pipe()
    p = Process(target=last_core_loop, args=(child_conn, [last_core], last_core_usage))
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
