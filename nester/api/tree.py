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

class Tree(Cloud):
     
    tag = None
    name = None   

    def __init__(self, auth, tag=None):
        super(Tree, self).__init__('trees', auth)
	self.tag = tag

    def new_copy(self, object):
        new_entity = Tree(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage trees')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='tree_command', help='Tree commands')

        list_cmd = app_cmd_parsers.add_parser('list', help='List trees')    
        list_cmd.add_argument('-f', '--forest', type=str, required=True, help='Forest id or tag')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle tree command")
            cmd_handled = True
            if (args.tree_command == 'list'):
               self.list(args.forest)
            elif (args.tree_command == 'clear'):
	       self.clear_cache()
	    else:
               cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def list(self, forest_id):
        try:
            self.query_list("forests/{0}/trees".format(forest_id))
            self.draw_table()
	except Exception as e:
            print(e)

    def load(self):
	return self.load_by_key(self.tag)

    def save(self):
        return self.save_by_key(self.tag)

    def draw_table_col_width(self, table):
        table.set_cols_width([20, 30])

    def draw_table_col_align(self, table):
        table.set_cols_align(["l", "r"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t"])

    def get_table_col_header(self):
        return ["tag", "name"]

    def get_table_row_data(self, tag):
        print_obj = Tree(self.auth, tag)
        print_obj.load()
        return [ print_obj.tag, print_obj.name ]


