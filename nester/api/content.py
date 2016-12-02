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
from subprocess import Popen, PIPE, STDOUT

from thing import Thing

class Content(Thing):

    def __init__(self, thing):
        self._thing = thing

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser('content', help='Manage current app\'s contents')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='content_command', help='content commands')

        push_cmd = app_cmd_parsers.add_parser('push', help='Push content to the remote live site')
        push_cmd.add_argument('-t', '--timeout', type=int, default=30, required=False, help='The timeout')

        pull_cmd = app_cmd_parsers.add_parser('pull', help='Pull content from the remote live site')
        pull_cmd.add_argument('-t', '--timeout', type=int, default=30, required=False, help='The timeout')

        app_cmd_parsers.add_parser('edit', help='Edit content on the remote live site')
        #permit_subparserss.add_parser('info',  help='Show current permit')
        #permit_subparserss.add_parser('deny',  help='Deny current user to enter the forest')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == 'content':
            self.log("handle content command")
            cmd_handled = True
            if (args.content_command == 'push'):
               self.push(args.timeout)
	    elif (args.content_command == 'pull'):
               self.pull(args.timeout)
	    elif (args.content_command == 'edit'):
               self.edit()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled
   
    def push(self, timeout):
	self.log("push content up")
        self.os_exec("/usr/bin/rsync -avzrh --timeout=" + str(timeout) + " --progress /var/app nest:/var")

    def pull(self, timeout):
	self.log("pull content up")
        self.os_exec("/usr/bin/rsync -avzrh --timeout=" + str(timeout) + " --progress nest:/var/app /var")

    def edit(self):
	self.log("edit content")
	os.system("ssh nest")

