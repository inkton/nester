#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT

from cloud import Cloud

class Content(Cloud):

    def __init__(self, auth):
        super(Cloud, self).__init__('content', auth)

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser('content', help='Manage contents')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='content_command', help='Content commands')

        push_cmd = app_cmd_parsers.add_parser('push', help='Push content to the remote live site')
        push_cmd.add_argument('-t', '--timeout', type=int, default=30, required=False, help='The timeout')

        pull_cmd = app_cmd_parsers.add_parser('pull', help='Pull content from the remote live site')
        pull_cmd.add_argument('-t', '--timeout', type=int, default=30, required=False, help='The timeout')

        app_cmd_parsers.add_parser('edit', help='Edit content on the remote live site')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle content command")
            cmd_handled = True
            if (args.content_command == 'push'):
               self.push(args.timeout)
	    elif (args.content_command == 'pull'):
               self.pull(args.timeout)
	    elif (args.content_command == 'edit'):
               self.edit()
            elif (args.content_command == 'clear'):
	       self.clear_cache()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled
   
    def push(self, timeout):
	self.log("push content up")
        if (os.environ['NEST_PLATFORM_TAG'] != 'worker'):
            self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.push_excludes --timeout=" + str(timeout) + " --progress /var/app/app.nest /nest:/var/app")
            self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.push_excludes --timeout=" + str(timeout) + " --progress /var/app/app.json /nest:/var/app")
            self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.push_excludes --timeout=" + str(timeout) + " --progress /var/app/app/nest /nest:/var/app")
        self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.push_excludes --timeout=" + str(timeout) + " --progress " + os.environ['NEST_FOLDER_SOURCE'] + " /nest:/var/app/source")

    def pull(self, timeout):
	self.log("pull content up")
        if (os.environ['NEST_PLATFORM_TAG'] != 'worker'):
            self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.pull_excludes --timeout=" + str(timeout) + " --progress nest:/var/app/app.nest /var/app")
            self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.pull_excludes --timeout=" + str(timeout) + " --progress nest:/var/app/app.json /var/app")
            self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.pull_excludes --timeout=" + str(timeout) + " --progress nest:/var/app/nest /var/app")
	    self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.pull_excludes --timeout=" + str(timeout) + " --progress nest:/var/app/log /var/app")
        self.os_exec("/usr/bin/rsync -avzrh --exclude-from=/var/app/.pull_excludes --timeout=" + str(timeout) + " --progress nest:" + os.environ['NEST_FOLDER_SOURCE'] + " /var/app/source")

    def edit(self):
	self.log("edit content")
	os.system("ssh nest")

