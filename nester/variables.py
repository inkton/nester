#

import sys

__version__ = "0.1.0"

# set configuration file path depending on sys.exec_prefix
# on *Linux sys.exec_prefix = '/usr' and default path must be in '/etc'
# on *BSD sys.exec_prefix = '/usr/{pkg,local}/' and default path
# is '/usr/{pkg,local}/etc'
if sys.exec_prefix != '/usr':
    # for *BSD
    conf_prefix = sys.exec_prefix
else:
    # for *Linux
    conf_prefix = ''

configfile = conf_prefix + '/etc/nester.conf'

