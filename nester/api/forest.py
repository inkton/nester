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
    continent = None

    def __init__(self, auth, tag=None):
        super(Forest, self).__init__('forests', auth)
	self.tag = tag

    def new_copy(self, object):
        new_entity = Forest(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage forests')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='forest_command', help='Forest commands')

        app_cmd_parsers.add_parser('list', help='List forests')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle forest command")
            cmd_handled = True
            if (args.forest_command == 'list'):
               self.list()
            elif (args.forest_command == 'clear'):
	       self.clear_cache()
	    else:
               cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def list(self):
        try:
            self.query_list()
            self.draw_table()
	except Exception as e:
            print(e)

    def load(self):
	self.load_by_key(self.tag, self)

    def save(self):
        self.save_by_key(self.tag, self)

    def draw_table_col_width(self, table):
        table.set_cols_width([20, 10, 30, 10])

    def draw_table_col_align(self, table):
        table.set_cols_align(["l", "r", "r", "r"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m", "m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t", "t", "t"])

    def get_table_col_header(self):
        return ["tag", "kind", "name", "continent"]

    def get_table_row_data(self, tag):
        print_obj = Forest(self.auth, tag)
        print_obj.load()
        return [ print_obj.tag, print_obj.kind, print_obj.name, print_obj.continent ]


