import argparse
import os
import signal
import time

import backend
from database import DataBase

def start_test(args):
    # Open IP list file
    pid = os.fork()
    if pid != 0:
        return
    with open(args.ip_list, "r") as f:
        node_list = f.read()
        node_list.strip()
        node_list = node_list.split("\n")

        # TODO: check IP pattern
        node_list = [ ip.strip() for ip in node_list ]

        backend.launch(node_list, args.db)
        
def stop_test(args):
    # Get backend pid from DataBase
    # Then terminate it
    db = DataBase(args.db)
    pid = db.get_pid()
    if pid < 0:
        print("No test is running")
    else:
        os.kill(pid, signal.SIGTERM)


def monitor_test(args):
    db = DataBase(args.db)
    pid = db.get_pid()
    if pid < 0:
        print("No test is running")
        return
    
    while True:
        s = db.format_info()
        s += db.format_top()
        os.system("clear")
        print(s)
        time.sleep(1)

def view_test(args):
    db = DataBase(args.db)
    delim = "=" * 10 + "\n"
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
    parser_start.add_argument("--db", "-db", default="roce.db", dest="db", help="the path of database")
    parser_start.set_defaults(func=start_test)


    # stop
    # TODO: how to stop?
    parser_stop = subparsers.add_parser("stop", help="stop a test")
    parser_stop.add_argument("--db", "-db", default="roce.db", dest="db", help="the path of database")
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
