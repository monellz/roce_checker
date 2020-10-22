import argparse
import os
import signal
import time
import subprocess

import backend
from database import DataBase

def start_test(args):
    # Clean previous infomation
    db = DataBase(args.db)
    db.clear()
    db.close()

    pid = os.fork()
    if pid != 0:
        return
    with open(args.ip_list, "r") as f:
        node_list = f.read()
        node_list = node_list.strip()
        node_list = node_list.split("\n")

        # TODO: check IP pattern
        
        if args.exclude_ip_list is not None:
            with open(args.exclude_ip_list, "r") as ef:
                node_list = set([ ip.strip() for ip in node_list ])
                exclude_list = ef.read()
                exclude_list = exclude_list.strip()
                exclude_list = exclude_list.split('\n')
                exclude_list = set([ ip.strip() for ip in exclude_list ])
                node_list = node_list.difference(exclude_list)
                node_list = list(node_list)

        print(node_list)
        backend.launch(node_list, args.db)
        
def stop_test(args):
    # Get backend pid from DataBase
    # Then terminate it
    db = DataBase(args.db)
    pid = db.get_pid()
    if args.force:
        if pid > 0: os.kill(pid, signal.SIGTERM)
        subprocess.call(['./script/manual_kill.sh'], shell=False)
    else:
        if pid < 0:
            print("No test is running")
        else:
            os.kill(pid, signal.SIGTERM)


def monitor_test(args):
    db = DataBase(args.db)
    try:
        while True:
            s = db.format_info()
            s += db.format_top()
            os.system("clear")
            print(s)
            time.sleep(1)
    except KeyboardInterrupt:
        return

def view_test(args):
    db = DataBase(args.db)
    delim = "=" * 20 + "\n"
    s = delim
    s += "UCX TEST Result\n"
    s += db.format_ucx_test()
    s += delim
    s += "Perf TEST Result\n"
    s += db.format_perf_test()
    s += delim
    print(s)

def roce_info(args):
    print('please run "rocectl {positional argument} --help" to see guidance')


def parse_args():
    parser = argparse.ArgumentParser(prog="rocectl", description="use rocectl command to control RoCE environment test")
    parser.set_defaults(func=roce_info)
    subparsers = parser.add_subparsers()

    # start
    parser_start = subparsers.add_parser("start", help="start a new test");
    parser_start.add_argument("--ip_list", "-f", required=True, dest="ip_list", help="the path of ip list")
    parser_start.add_argument("--exclude_ip_list", "-e", dest="exclude_ip_list", help="the path of exclude ip list")
    parser_start.add_argument("--db", "-db", default="roce.db", dest="db", help="the path of database")
    parser_start.set_defaults(func=start_test)


    # stop
    # TODO: how to stop?
    parser_stop = subparsers.add_parser("stop", help="stop a test")
    parser_stop.add_argument("--db", "-db", default="roce.db", dest="db", help="the path of database")
    parser_stop.add_argument("--force", "-f", action="store_true", dest="force", help="kill all related processes")
    parser_stop.set_defaults(func=stop_test)


    # top
    parser_top = subparsers.add_parser("top", help="monitor the test")
    parser_top.add_argument("--db", "-db", default="roce.db", dest="db", help="the path of database")
    parser_top.set_defaults(func=monitor_test)

    
    # view
    parser_view = subparsers.add_parser("view", help="display data")
    parser_view.add_argument("--db", "-db", default="roce.db", dest="db", help="the path of database")
    parser_view.set_defaults(func=view_test)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    parse_args() 
