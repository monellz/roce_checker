#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import multiprocessing
import time
import subprocess
from enum import Enum

from database import DataBase, now

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


class TaskKind(Enum):
    NOPWCHECK   = 'no_passwork_check'
    ENVCHECK    = 'env_check'
    SETUP       = 'setup'
    CONNCHECK   = 'connection_check'
    UCXTEST     = 'ucx_test'
    PERFV2TEST  = 'perf_v2_test'

class Task:
    def __init__(self, kind, ip, port=None):
        self.kind = kind
        self.ip   = ip
        self.port = port

    def __call__(self):
        return '{} - ip: {}'.format(self.kind, self.ip)

    def __str__(self):
        return '{} - ip: {},'.format(self.kind, self.ip)

class Result:
    # Kind
    WAIT   = 'waiting'
    ACCEPT = 'running'
    SUCC   = 'successful'
    FAILED = 'failed'

    def __init__(self, kind, ip, code, stdout=None, stderr=None):
        self.kind = kind
        self.ip   = ip
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
    
    def __str__(self):
        return '{} - ip: {}, code: {}'.format(self.kind, self.ip, self.code)


class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, res_path, target_path):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

        # res_path: Path of result directory in master machine
        # target_path: Path of directory in remote machine
        self.res_path = res_path
        self.target_path = target_path

    def run(self):
        proc_name = self.name
        while True:
            task = self.task_queue.get()
            if task is None:
                # Poison pill means shutdown
                #print('{}: Exiting'.format(proc_name))
                self.task_queue.task_done()
                break

            # ACCEPT the task
            accept_result = Result(task.kind, ip=task.ip, code=Result.ACCEPT)
            self.result_queue.put(accept_result)
            
            out_path = os.path.join(self.res_path, task.kind.value)
            if task.kind == TaskKind.NOPWCHECK:
                cmd = './nopassword_check.sh {}'.format(task.ip)
            elif task.kind == TaskKind.ENVCHECK:
                cmd = './env_check.sh {} {}'.format(task.ip, out_path)
            elif task.kind == TaskKind.SETUP:
                cmd = './setup.sh {} {} {}'.format(task.ip, out_path, self.target_path)
            elif task.kind == TaskKind.CONNCHECK:
                ip1, ip2 = task.ip[0], task.ip[1]
                cmd = './connection_check.sh {} {} {}'.format(ip1, ip2, out_path)
            elif task.kind == TaskKind.UCXTEST:
                ip1, ip2 = task.ip[0], task.ip[1]
                port = task.port
                cmd = './ucx_test.sh {} {} {} {} {}'.format(ip1, ip2, port, out_path, self.target_path)
                print(cmd)
            elif task.kind == TaskKind.PERFV2TEST:
                ip1, ip2 = task.ip[0], task.ip[1]
                port = task.port
                cmd = './perf_v2_test.sh {} {} {} {} {}'.format(ip1, ip2, port, out_path, self.target_path)
                print(cmd)
            else:
                raise NotImplementedError

            stdout, stderr, exit_code = exec_cmd(cmd)

            if exit_code == 0:
                result = Result(kind=task.kind, ip=task.ip, code=Result.SUCC, stdout=stdout, stderr=stderr)
            else:
                result = Result(kind=task.kind, ip=task.ip, code=Result.FAILED, stdout=stdout, stderr=stderr)

            self.task_queue.task_done()
            self.result_queue.put(result)

class Producer(multiprocessing.Process):

    def __init__(self, nodes_ip, num_consumers, db_path, result_path="./.roce_result", target_path="/root/.roce"):
        multiprocessing.Process.__init__(self)
        self.nodes_ip = nodes_ip
        self.result_path = result_path
        self.target_path = target_path
        self.num_consumers = num_consumers

        self.db = DataBase(db_path)
    
    def run(self):
        # Store pid, date into DataBase
        self.db.update_info(self.pid, now())

        # Init node status
        nodes_status = {}
        for ip in self.nodes_ip:
            nodes_status[ip] = None

        # Establish communication queues
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        # Create result path
        remove_dir(self.result_path)
        make_dir(self.result_path)
        for kind in TaskKind:
            make_dir(os.path.join(self.result_path, kind.value))

        # Start consumers
        print('Creating {} consumers'.format(self.num_consumers))
        consumers = [
            Consumer(tasks, results, self.result_path, self.target_path)
            for _ in range(self.num_consumers)
        ]

        for w in consumers:
            w.daemon = True
            w.start()
        
        # Start Time
        print("Test Start at {}".format(now()))

        # Number of Task have enqueue
        ntasks = 0

        # Enqueue task first - "no password check"
        for ip in self.nodes_ip:
            tasks.put(Task(kind=TaskKind.NOPWCHECK, ip=ip))
            nodes_status[ip] = TaskKind.NOPWCHECK
            # +2 because there is ACCEPT and SUCC -> two result
            ntasks += 2
            self.db.update_top(ip, TaskKind.NOPWCHECK, Result.WAIT, now())
        
        conn_check_waiting_list = []
        
        # Generate port List for ucx test
        # [1001, 1002, ..., 1000+len(nodes_ip)]
        port_list = [1001+i for i in range(0, len(self.nodes_ip))]
        UCX_test_nodes_info = {}
        for ip in self.nodes_ip:
            UCX_test_nodes_info[ip] = {}
            UCX_test_nodes_info[ip]['occupied'] = False
            UCX_test_nodes_info[ip]['dep_list'] = []
        

        while ntasks > 0:
            result = results.get()
            ntasks -= 1

            print('Result: {}'.format(result))

            if result.code == Result.SUCC:
                # enqueue more task
                if result.kind == TaskKind.NOPWCHECK:
                    tasks.put(Task(kind=TaskKind.ENVCHECK, ip=result.ip))
                    nodes_status[result.ip] = TaskKind.ENVCHECK
                    ntasks += 2
                    self.db.update_top(result.ip, TaskKind.ENVCHECK, Result.WAIT, now())

                elif result.kind == TaskKind.ENVCHECK:
                    tasks.put(Task(kind=TaskKind.SETUP, ip=result.ip))
                    nodes_status[result.ip] = TaskKind.SETUP
                    ntasks += 2
                    self.db.update_top(result.ip, TaskKind.SETUP, Result.WAIT, now())

                elif result.kind == TaskKind.SETUP:
                    self.db.delete_top(result.ip)
                    for ip in conn_check_waiting_list:
                        ip1, ip2 = (result.ip, ip) if result.ip < ip else (ip, result.ip)
                        tasks.put(Task(kind=TaskKind.CONNCHECK, ip=[ip1, ip2]))
                        ntasks += 2
                        self.db.update_top([result.ip, ip], TaskKind.CONNCHECK, Result.WAIT, now())
                    conn_check_waiting_list.append(result.ip)
                    nodes_status[result.ip] = TaskKind.CONNCHECK
                
                elif result.kind == TaskKind.CONNCHECK:
                    ip1 = result.ip[0]
                    ip2 = result.ip[1]

                    if UCX_test_nodes_info[ip1]['occupied'] is False and \
                        UCX_test_nodes_info[ip2]['occupied'] is False:
                        # both ip is available
                        idx = (self.nodes_ip.index(ip1) + self.nodes_ip.index(ip2)) % len(self.nodes_ip)
                        port = port_list[idx]

                        tasks.put(Task(kind=TaskKind.UCXTEST, ip=[ip1, ip2], port=port))
                        ntasks += 2
                        
                        # Occupied
                        UCX_test_nodes_info[ip1]['occupied'] = True
                        UCX_test_nodes_info[ip2]['occupied'] = True
                    else:
                        # at lease have one ip is not available
                        UCX_test_nodes_info[ip1]['dep_list'].append(ip2)
                        UCX_test_nodes_info[ip2]['dep_list'].append(ip1)

                elif result.kind == TaskKind.UCXTEST:
                    ip1 = result.ip[0]
                    ip2 = result.ip[1]
                    
                    UCX_test_nodes_info[ip1]['occupied'] = False
                    UCX_test_nodes_info[ip2]['occupied'] = False

                    # if do not have other ucx task (dependent edge), do the perf_v2_test
                    # if len(UCX_test_nodes_info[ip1]['dep_list']) == 0 and \
                    #     len(UCX_test_nodes_info[ip2]['dep_list']) == 0:

                    # Do perf_v2_test
                    idx = sum([self.nodes_ip.index(ip) for ip in [ip1, ip2]]) % len(self.nodes_ip)
                    port = port_list[idx]
                    tasks.put(Task(kind=TaskKind.PERFV2TEST, ip=[ip1, ip2], port=port))
                    ntasks += 2

                    # Find dependence, and Enqueue new task
                    for ipx in result.ip:
                        if len(UCX_test_nodes_info[ipx]['dep_list']) > 0:
                            for ipy in UCX_test_nodes_info[ipx]['dep_list']:
                                if UCX_test_nodes_info[ipy]['occupied'] is False:
                                    ip1, ip2 = (ipx, ipy) if ipx < ipy else (ipy, ipx)
                                    idx = sum([self.nodes_ip.index(ip) for ip in [ip1, ip2]]) % len(self.nodes_ip)
                                    port = port_list[idx]

                                    tasks.put(Task(kind=TaskKind.UCXTEST, ip=[ip1, ip2], port=port))
                                    ntasks += 2
                                    
                                    # Occupied
                                    UCX_test_nodes_info[ip1]['occupied'] = True
                                    UCX_test_nodes_info[ip2]['occupied'] = True

                                    # Remove from List
                                    UCX_test_nodes_info[ip1]['dep_list'].remove(ip2)
                                    UCX_test_nodes_info[ip2]['dep_list'].remove(ip1)

                                    break

                    # Maybe have to enqueue more task



            elif result.code == Result.FAILED:
                if type(result.ip) == str:
                    nodes_status[result.ip] = Result.FAILED
                    self.db.update_top(result.ip, result.kind, Result.FAILED, now())
                else:
                    pass

            elif result.code == Result.ACCEPT:
                # Update database
                self.db.update_top(result.ip, result.kind, Result.ACCEPT, now())
            

        print("Producer ntasks = {}, prepare to join".format(ntasks))
        # Wait for all of the tasks to finish
        tasks.join()

        # Add a poison pill for each consumer
        for _ in range(self.num_consumers):
            tasks.put(None)


        

def launch(nodes_ip, db_path):
    nodes_ip    = [
        '172.16.201.4',
        "172.16.201.5",
        "172.16.201.6",
        # "172.16.201.7",
        # "172.16.201.8",
        # "172.16.201.9",
        # "172.16.201.10",
        # "172.16.201.13",
        # "172.16.201.14",
        # "172.16.201.100",
    ] 
    producer = Producer(nodes_ip, 7, db_path)
    producer.start()