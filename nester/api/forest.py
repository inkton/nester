#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
from daemonize import Daemonize

from cloud import Cloud

class Forest(Cloud):
     
    tag = None
    name = None   
    kind = None   

    def __init__(self, auth, tag=None):
        super(Forest, self).__init__(auth)

	self.tag = tag

        try:
            os.makedirs(self.home + '/forests')
        except OSError as exception:
	    if exception.errno != errno.EEXIST:
                raise FailedValidation('Unable to create settings directory ' + self.home)

    def new_copy(self, object):
        new_entity = Forest(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser('forest', help='Manage forests')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='forest_command', help='forest commands')

        app_cmd_parsers.add_parser('list', help='List forests')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == 'forest':
            self.log("handle forest command")
            cmd_handled = True
            if (args.forest_command == 'list'):
               self.list()
	    else:
               cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def list(self):
        try:
            self.cache_list("forests")
	except Exception as e:
            print(e.value)

    def load(self):
	self.load_object('/forests/' + self.tag, self)

    def save(self):
        self.save_object('/forests/' + self.tag, self)

    def draw_table_col_header(self, table):
        table.add_rows([["tag",  "kind", "name"]])

    def draw_table_col_width(self, table):
        table.set_cols_width([10, 25, 30])

    def draw_table_col_align(self, table):
        table.set_cols_align(["c", "r", "r"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t", "t"])

    def draw_table_row_add(self, table, tag):
        print_obj = Forest(auth, tag)
        table.add_rows([[ print_obj.tag, print_obj.kind, print_obj.name]])


