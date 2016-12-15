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

class Domain(Cloud):
    
    id = None
    tag = None    
    name = None    
    aliases = None    

    def __init__(self, auth, tag=None):
        super(Domain, self).__init__('domains', auth)
	self.tag = tag

    def new_copy(self, object):
        new_entity = Domain(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage domains')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='domain_command', help='Domain commands')

        sub_cmd = app_cmd_parsers.add_parser('add', help='Add domain')
        sub_cmd.add_argument('-n', '--name', type=str, required=True, help='Name of the domain')
        sub_cmd.add_argument('-t', '--tag', type=str, required=True, help='A memorable identifier. Must be lower case without spaces')
        sub_cmd.add_argument('-a', '--aliases', type=str, required=False, help='A comma seperated list of aliases')
        
	sub_cmd = app_cmd_parsers.add_parser('remove', help='Remove domain')
        sub_cmd.add_argument('-t', '--tag', type=str, required=True, help='A domain tag')
        app_cmd_parsers.add_parser('list', help='List all domains')
          
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle domain command")
            cmd_handled = True
            if (args.domain_command == 'add'):
               self.add(args.tag, args.name, args.aliases)
            elif (args.domain_command == 'remove'):
               self.remove(args.tag)
            elif (args.domain_command == 'list'):
               self.list()
            elif (args.domain_command == 'clear'):
	       self.clear_cache()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled
 
    def add(self, tag, name, aliases):
        try:
            self.create("apps/{0}/domains".format(os.environ['NEST_APP_ID']), 
			{'tag' : tag, 
			'name' : name,
			'aliases' : aliases })
	except Exception as e:
            print(e)

    def remove(self, tag):
        try:
            if (self.confirm("Are you sure to remove the domain " + tag +
		" ?\n", default="no")) :
		self.cache_list("apps/{0}/domains".format(
		  os.environ['NEST_APP_ID']), 
		  None, 'tag')

	        remove_obj = Domain(self.auth, tag)
        	if not remove_obj.load():
                   print "The domain does not exist"
                   return
 
		self.delete("apps/{0}/domains/{1}".format(
		  os.environ['NEST_APP_ID'],
		  remove_obj.id), {})
	except Exception as e:
            print(e)

    def list(self):
	self.log("current nest")
        try:
            self.cache_list("apps/{0}/domains".format(
		os.environ['NEST_APP_ID']), 
			None, 'tag')
            self.draw_table()
	except Exception as e:
            print(e)

    def load(self):
	return self.load_by_key(self.tag)

    def save(self):
        return self.save_by_key(self.tag)

    def draw_table_col_width(self, table):
        table.set_cols_width([5, 12, 20, 35])

    def draw_table_col_align(self, table):
        table.set_cols_align(["c", "r", "r", "l"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m", "m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t", "t", "t"])

    def get_table_col_header(self):
        return ["id", "tag", "name", "aliases" ]

    def get_table_row_data(self, tag):
        print_obj = Domain(self.auth, tag)
        print_obj.load()
        return [  print_obj.id, print_obj.tag, 
		print_obj.name, 
		print_obj.aliases ]

