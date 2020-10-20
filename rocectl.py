import argpase

def start_test(args):
    pass

def stop_test(args):
    pass

def moniter_test(args):
    pass

def view_test(args):
    pass


def parse_args():
    parser = argparse.ArgumentParser(prog="rocectl", description="use rocectl command to control RoCE environment test")
    subparsers = parser.add_subparsers()

    # start
    parser_start = subparsers.add_parser("start", help="start a new test");
    parser_start.add_argument("--ip_list", "-f", required=True, dest="ip_list", help="the path of ip list")
    parser_start.add_argument("--id", "-i", dest="id", help="test/file id")
    parser_start.set_defaults(func=start_test)


    # stop
    # TODO: how to stop?
    parser_stop = subparsers.add_parser("stop", help="stop a test")
    parser_top.set_defaults(func=stop_test)


    # top
    parser_top = subparsers.add_parser("top", help="monitor the test")
    parser_top.set_defaults(func=monitor_test)

    
    # view
    parser_view = subparser.add_parser("view", help="display data")
    parser_top.set_defaults(func=view_test)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    parse_args() 
