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

class Data(Cloud):

    def __init__(self, auth):
        super(Data, self).__init__('data', auth)

    def new_copy(self, object):
        new_entity = Data(self.auth) 
        new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage the data')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='data_command', help='Data commands')

        app_cmd_parsers.add_parser('pull', help='Pull data')
        app_cmd_parsers.add_parser('push', help='Push data')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle data command")
            cmd_handled = True
            if (args.data_command == 'pull'):
                self.pull()
            elif (args.data_command == 'push'):
                self.push()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def pull(self):
        try:
            self.os_exec("ssh nest '/usr/sbin/save-db'", False)
        except Exception as e:
            print(e)

    def push(self):
        try:
            self.os_exec("ssh nest '/usr/sbin/load-db'", False)
        except Exception as e:
            print(e)
