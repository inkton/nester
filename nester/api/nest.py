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

from thing import Thing

def run_nest():
   os.system("NEST_OPERATION=start /var/app/app.nest")

class Nest(Thing):

    def __init__(self, thing):
        self._thing = thing

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser('nest', help='Manage the nest')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='nest_command', help='nest commands')

        app_cmd_parsers.add_parser('up', help='Launch the nest')
        app_cmd_parsers.add_parser('down', help='Teardown the nest')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == 'nest':
            self.log("handle nest command")
            cmd_handled = True
            if (args.nest_command == 'up'):
               self.up()
            elif (args.nest_command == 'down'):
               self.down()
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
        except:
	      pass

