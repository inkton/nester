#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidt=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
from daemonize import Daemonize

from cloud import Cloud

class DevKit(Cloud):
     
    def __init__(self, auth):
        super(DevKit, self).__init__('devkits', auth)

    def new_copy(self, object):
        new_entity = DevKit(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage devKits')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='devkit_command', help='DevKit commands')

        sub_cmd = app_cmd_parsers.add_parser('send', help='Send a devkit')    
        sub_cmd.add_argument('-i', '--id', type=int, required=True, help='Id of the contact')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle devkit command")
            cmd_handled = True
            if (args.devkit_command == 'send'):
               self.send(args.id)
	    else:
               cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def send(self, id):
        try:
            self.create("users/{0}/apps/{1}/contacts/{2}/devkit".format(
		os.environ['NEST_CONTACT_USER_ID'],
		os.environ['NEST_APP_ID'],
		id), {})
	except Exception as e:
            print(e)

