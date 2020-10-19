import os
import time
import argparse
from itertools import combinations
from multiprocessing import Process, Pool
import subprocess

def get_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def exec_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    return stdout, stderr, exit_code


def run(args):
    NUM_PROC_PARALLEL = 5

    nodes_ip    = [1,2,3,4,5]
    server_ip   = 1
    
    # Start Time
    st = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print("Test Start at {}".format(st))

    # check whether exist result save file, if not then create
    result_path = ".rose_result"
    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    # ====================
    # No password check
    # ====================
    pool = Pool(processes=NUM_PROC_PARALLEL)
    results = []

    for ip in nodes_ip:
        cmd = 'bash nopassword_check.sh {} {}'.format(ip, server_ip)
        res = pool.apply_async(exec_cmd, (cmd,))
        results.append(res)

    pool.close()
    pool.join()
    
    # Handle No password check result
    for ip, res in zip(nodes_ip, results):
        _, _, exit_code = res.get()
        if exit_code == 1:
            print("{} no password check fail".format(ip))
            nodes_ip.remove(ip)

    # ====================
    # Env check
    # ====================
    pool = Pool(processes=NUM_PROC_PARALLEL)
    results = []

    for ip in nodes_ip:
        cmd = 'bash env_check.sh {} {}'.format(ip, os.path.join(result_path, "./env_check"))
        res = pool.apply_async(exec_cmd, (cmd,))
        results.append(res)

    pool.close()
    pool.join()
    
    # Handle Env check result
    for ip, res in zip(nodes_ip, results):
        _, _, exit_code = res.get()
        if exit_code == 1:
            print("{} Env check fail".format(ip))
            nodes_ip.remove(ip)

    # ====================
    # Setup
    # ====================
    pool = Pool(processes=NUM_PROC_PARALLEL)
    results = []

    for ip in nodes_ip:
        cmd = 'bash setup.sh {} {} {}'.format(ip, "/.roce_check/setup", os.path.join(result_path, "./setup"))
        res = pool.apply_async(exec_cmd, (cmd,))
        results.append(res)

    pool.close()
    pool.join()
    
    # Handle Setup result
    for ip, res in zip(nodes_ip, results):
        _, _, exit_code = res.get()
        if exit_code == 1:
            print("{} Env Setup fail".format(ip))
            nodes_ip.remove(ip)

    # ===================
    # Connection check
    # parallel, the number of iters is C(n, 2)
    # ====================
    pool = Pool(processes=NUM_PROC_PARALLEL)
    results = []

    comb = list(combinations(nodes_ip, 2))
    for ip1, ip2 in comb:
        cmd = 'bash connection_check.sh {} {} {} {}'.format(ip1, ip2, "/.roce_check/connection_check", os.path.join(result_path, "./connection_check"))
        res = pool.apply_async(exec_cmd, (cmd,))
        results.append(res)
    
    pool.close()
    pool.join()

    # Handle connection check result
    for c, res in zip(comb, results):
        _, _, exit_code = res.get()
        if exit_code == 1:
            print("{} <-> {} connection fail".format(c[0],c[1]))


    # Other check
    # for ip1, ip2 in comb:


if __name__ == "__main__":
    args = get_args()
    run(args)
