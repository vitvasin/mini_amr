import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/smr/workspaces/mini_amr/amrROS2_ws/install/python_pkg'
