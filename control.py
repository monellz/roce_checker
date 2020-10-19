#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

def make_dir(path):
    # check whether exist result save file, if not then create
    if not os.path.isdir(path):
        os.mkdir(path)

def remove_dir(path):
    os.system('rm -rf {}'.format(path))

def run(args):
    NUM_PROC_PARALLEL = 5

    nodes_ip    = [
        '172.16.201.4',
        "172.16.201.5",
        "172.16.201.6",
        "172.16.201.7",
        "172.16.201.8",
        "172.16.201.9",
        "172.16.201.10",
        "172.16.201.13",
        # "172.16.201.14",
        "172.16.201.100",
    ]

    failed_ip   = []
    
    # Start Time
    st = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print("Test Start at {}".format(st))

    # result path
    result_path = "./.rose_result"
    remove_dir(result_path)
    make_dir(result_path)

    # ====================
    # No password check
    # ====================
    pool = Pool(processes=NUM_PROC_PARALLEL)
    def nopw_check_handle_func(ip):
        def f(ret):
            stdout, stderr, exit_code = ret
            if exit_code != 0:
                print("{} no password check fail.".format(ip))
                nodes_ip.remove(ip)
            else:
                print("{} no password check successfully.".format(ip))
        return f

    results = []
    for ip in nodes_ip:
        cmd = './nopassword_check.sh {}'.format(ip)
        res = pool.apply_async(exec_cmd, args=(cmd,), callback=nopw_check_handle_func(ip))
        results.append(res)

    for res in results:
        res.wait()

    # ====================
    # Env check
    # ====================
    env_check_result_path = os.path.join(result_path, "./env_check")
    make_dir(env_check_result_path)

    def env_check_handle_func(ip):
        def f(ret):
            stdout, stderr, exit_code = ret
            if exit_code != 0:
                print("{} Env check fail".format(ip))
                nodes_ip.remove(ip)
            else:
                print("{} Env check successfully.".format(ip))
        return f

    results = []
    for ip in nodes_ip:
        cmd = './env_check.sh {} {}'.format(ip, env_check_result_path)
        res = pool.apply_async(exec_cmd, args=(cmd,), callback=env_check_handle_func(ip))
        results.append(res)

    for res in results:
        res.wait()

    # ====================
    # Setup
    # ====================
    setup_result_path = os.path.join(result_path, "./setup")
    make_dir(setup_result_path)

    def setup_handle_func(ip):
        def f(ret):
            stdout, stderr, exit_code = ret
            if exit_code != 0:
                print("{} Setup fail".format(ip))
                nodes_ip.remove(ip)
            else:
                print("{} Setup successfully.".format(ip))
        return f

    results = []
    for ip in nodes_ip:
        cmd = './setup.sh {} {} {}'.format(ip, "/.roce_check/setup", setup_result_path)
        res = pool.apply_async(exec_cmd, args=(cmd,), callback=setup_handle_func(ip))
        results.append(res)

    for res in results:
        res.wait()

    # ===================
    # Connection check
    # parallel, the number of iters is C(n, 2)
    # ====================
    conn_check_result_path = os.path.join(result_path, "./connection_check")
    make_dir(conn_check_result_path)

    def conn_check_handle_func(ip1, ip2):
        def f(ret):
            stdout, stderr, exit_code = ret
            if exit_code != 0:
                print("{} <-> {} connection fail, exit code: {}".format(ip1, ip2, exit_code))
            else:
                print("{} <-> {} connection successfully.".format(ip1, ip2))
        return f

    results = []
    comb = list(combinations(nodes_ip, 2))
    for ip1, ip2 in comb:
        cmd = './connection_check.sh {} {} {}'.format(ip1, ip2, conn_check_result_path)
        res = pool.apply_async(exec_cmd, args=(cmd,), callback=conn_check_handle_func(ip1, ip2))
        results.append(res)
    
    pool.close()
    pool.join()


    # Other check


if __name__ == "__main__":
    args = get_args()
    run(args)
