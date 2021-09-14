# import pdb
import sys

import server


old_sys_exit = sys.exit


def new_sys_exit(value):
    pdb.set_trace()
    old_sys_exit(value)


# sys.exit = new_sys_exit


if __name__ == "__main__":
    server.main()
