#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT

from thing import FailedValidation
from cloud import Cloud
from auth import Auth

class Deployment(Cloud):

    def __init__(self, auth):
        super(Deployment, self).__init__('deployments', auth)

    def new_copy(self, object):
        new_entity = Deployment(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage the deployment')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='dep_command', help='Deployment commands')

        app_cmd_parsers.add_parser('update', help='Deploy the latest structural changes')

    def exec_command(self, args):
	self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
 	    self.log("handle deployment command")
            cmd_handled = True
            if (args.dep_command == 'update'):
               self.change()
            else:
            	cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def change(self):
        try:
	    if (self.confirm("This will deploy the latest structural changes.\n"+
               "Make sure the code has been checked-in and properly backed up.\n"+ 
               "A new devkit will be emailed. Use the updated devkit for any\n"+ 
               "further work", default="no")) :
            	data = self.update("apps/{0}/deployment".
			format(os.environ['NEST_APP_ID']), {})

	except Exception as e:
            print(e)



