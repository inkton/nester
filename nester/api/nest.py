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

def run_nest():
   os.system("NEST_OPERATION=start /var/app/app.nest")

class Nest(Cloud):
    
    id = None    
    tag = None    
    status = None
    name = None    
    host_platform_tag = None    

    def __init__(self, auth, tag=None):
        super(Nest, self).__init__('nests', auth)
	self.tag = tag

    def new_copy(self, object):
        new_entity = Nest(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage nests')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='nest_command', help='Nest commands')

        app_cmd_parsers.add_parser('up', help='Launch this nest')
        app_cmd_parsers.add_parser('down', help='Teardown this nest')
        app_cmd_parsers.add_parser('current', help='Show the current nest')
        app_cmd_parsers.add_parser('list', help='List all app nests')
          
        sub_cmd = app_cmd_parsers.add_parser('add', help='Add a nest')
        sub_cmd.add_argument('-t', '--tag', type=str, required=True, help='A memorable identifier. Must be lower case without spaces')
        sub_cmd.add_argument('-p', '--platform', choices=['web.net', 'web-socket.net', 'worker.net'], required=True, help='Nest platform [web.net, web-socket.net or worker.net] ')
        sub_cmd.add_argument('-n', '--name', type=str, required=True, help='Nest name')
        sub_cmd.add_argument('-s', '--scale', type=int, required=True, help='Nest scale size, the number of cushions')
        sub_cmd.add_argument('-z', '--scale-size', choices=['32m','64m','128m','256m','512m','1g','2g','4g','8g','16g'], required=True, help='Nest scale size, the number of cushions')

        sub_cmd = app_cmd_parsers.add_parser('remove', help='Remove a nest')
        sub_cmd.add_argument('-i', '--identifier', type=str, required=True, help='A nest tag or id')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle nest command")
            cmd_handled = True
            if (args.nest_command == 'up'):
               self.up()
            elif (args.nest_command == 'down'):
               self.down()
            elif (args.nest_command == 'current'):
               self.current()
            elif (args.nest_command == 'list'):
               self.list()
            elif (args.nest_command == 'add'):
               self.add(args.tag, args.platform, args.name,
			args.scale, args.scale_size)
            elif (args.nest_command == 'remove'):
               self.remove(args.identifier)
            elif (args.nest_command == 'clear'):
	       self.clear_cache()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled
   
    def up(self):
	self.log("run nest")
        daemon = Daemonize(app="nest", pid="/tmp/nest.pid", action=run_nest)
        daemon.start()

    def down(self):
	self.log("stop nest")
        try:
	    pid=None
	    with open('/tmp/nest.pid', 'r') as content_file:
		pid = int(content_file.read())
	    os.killpg(os.getpgid(pid), 9)
            sleep(.1)
	except Exception as e:
            print(e)

    def current(self):
	self.log("current nest")
        try:
            data = self.query("apps/{0}/nests/{1}/".format(
		os.environ['NEST_APP_ID'],
		os.environ['NEST_ID']))
            self.draw_object(self.new_copy(data['nest']),
	          ['tag', 'status', 'name', 'host_platform_tag'],
                  {'tag': 'tag', 'status':'status', 'name':'name','host_platform_tag':'platform'})
	except Exception as e:
            print(e)

    def list(self):
	self.log("current nest")
        try:
            self.cache_list("apps/{0}/nests".format(
		os.environ['NEST_APP_ID']), 
			None, 'tag')
            self.draw_table()
	except Exception as e:
            print(e)

    def add(self, tag, platform, name, scale, scale_size):
        try:
            self.create("apps/{0}/nests".format(os.environ['NEST_APP_ID']), 
			{ 'tag' : tag, 'host_platform_tag' : platform, 
			'name' : name, 'scale' : scale, 
			'scale_size' : scale_size,
			'status' : 'active' })
	except Exception as e:
            print(e)

    def remove(self, tag):
        try:
            if (self.confirm("Are you sure to remove the nest " + tag +
		" ?\nThis will remove the nest and its contents", default="no")) :
		self.cache_list("apps/{0}/nests".format(
		  os.environ['NEST_APP_ID']), 
		  None, 'tag')

	        remove_obj = Nest(self.auth, tag)
        	if not remove_obj.load():
                   print "The nest does not exist"
                   return
 
		self.delete("apps/{0}/nests/{1}".format(
		  os.environ['NEST_APP_ID'],
		  remove_obj.id), {})
	except Exception as e:
            print(e)

    def load(self):
	return self.load_by_key(self.tag)

    def save(self):
        return self.save_by_key(self.tag)

    def draw_table_col_width(self, table):
        table.set_cols_width([5, 12, 10, 10, 20])

    def draw_table_col_align(self, table):
        table.set_cols_align(["c", "l", "l", "l", "l"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m", "m", "m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t", "t", "t", "t"])

    def get_table_col_header(self):
        return ["id", "tag", "status", "name", "host_platform_tag"]

    def get_table_row_data(self, tag):
        print_obj = Nest(self.auth, tag)
        print_obj.load()
        return [  print_obj.id, print_obj.tag, 
		print_obj.status,
		print_obj.name, 
		print_obj.host_platform_tag]
