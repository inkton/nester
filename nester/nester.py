#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Rajitha Wijayaratne (rajitha.wijayaratne-at-gmail.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.



#import errno, sys, signal, os, datetime, time, logging, shutil
#import json, jsonpickle
#import base64, hashlib, hmac 
#import requests, httplib
#import requests

#import subprocess, itertools

#from forest import Forest
#from nest import Nest
#from permit import Permit
#from notice import Notice
#from user import User
#from util import Util

#from util import FailedValidation

"""
    nester.py -h | --help
    nester.py --version
    nester.py permit (allow <user> <secret> | info | deny)
    nester.py user (info | update [] )
B
    nester.py forest (list | info | enter)    
    nester.py nest (list (languages|frameworks|apps|databases) |
                    create name with --platform (language|framework|app)  [--user-first-name=<fname> --user-surname=<sname> --user-email=<email> --domain=<domain> --instances=<inst>] --db (mysql | postgress| mongodb)
                    
                   create ( ( bare | language (php) | framework (laravel|symfony|nette) db (none | mysql | postgress| mongodb) ) | app (wordpress) )  [--user-first-name=<fname> --user-surname=<sname> --user-email=<email> --domain=<domain> --instances=<inst>] | 
                   delete <name> |
                   replicate <forest> [--tree=<tree> --instances=1] |
                   test <name> rig (create | delete) |
                   status <name> |
                   exec <name> <instance> <cmd> [--args=<args>] |
                   ssh <name> <instance>
                   )           
"""

# version
# permit
#   allow user secret
#   deny
# forest
#   list 
#   info
#   enter
# nest
#   images
#   create name --user-first-name, --user-surname --user-email --image --domain --memory --drive-space --php-processor --db-processor    
#   create-staging name
#   delete name
#   update name
#   shell-exec name cmd --args
#   move name forest --pref-tree
#   enter name
#   nest status name
#def become_tty_fg():
#	os.setpgrp()
#	hdlr = signal.signal(signal.SIGTTOU, signal.SIG_IGN)
#	#tty = os.open('/dev/tty', os.O_RDWR)
#	#os.tcsetpgrp(tty, os.getpgrp())
#	signal.signal(signal.SIGTTOU, hdlr)


#!/usr/bin/env python
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time
from api.thing import Thing
from api.app import App
from api.content import Content

class Nester(object):
    
    def __init__(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        parser = argparse.ArgumentParser(prog='nester')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
        parser.add_argument('-l', '--log', type=str, required=False, help='The output log file')
        subparsers = parser.add_subparsers(dest='command', help='sub commands')
	
	thing = Thing()

	app = App(thing)
        app.parse_command(subparsers)

	content = Content(thing)
        content.parse_command(subparsers)

        args = parser.parse_args()

	if app.exec_command(args) == True:
		return
	if content.exec_command(args) == True:
		return

