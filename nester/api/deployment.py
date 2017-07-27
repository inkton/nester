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
        super(Deployment, self).__init__('deployment', auth)

    def new_copy(self, object):
        new_entity = Deployment(self.auth) 
        new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage the deployment')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='dep_command', help='Deployment commands')

        app_cmd_parsers.add_parser('update', help='Deploy the latest structural changes')
        app_cmd_parsers.add_parser('publish', help='Publish the source in the remote folder')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle deployment command")
            cmd_handled = True
            if (args.dep_command == 'update'):
                self.change()
            elif (args.dep_command == 'publish'):
                self.publish()
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

    def publish(self):
        try:
            host = os.environ['NEST_CONTACT_ID'] + '@' + os.environ['NEST_APP_TAG']+".nestapp.yt"
            rsync_cmd = "/usr/bin/rsync -avzrhe 'ssh -i /var/app/.contact_key -o StrictHostKeyChecking=no' "            
            self.os_exec("rsync -r /tmp/source/ " + self.get_source_shared_folder())
            self.os_exec(rsync_cmd + " --exclude=.git --exclude=bin --exclude=obj --timeout=120 --progress " + self.get_source_shared_folder() + "/ "+ host +":" + self.get_source_shared_folder() + "/ ")
            self.os_exec(rsync_cmd + " --timeout=60 --progress /var/app/app.nest "+ host +":/var/app")
            self.os_exec(rsync_cmd + " --timeout=60 --progress /var/app/app.json "+ host +":/var/app")
            self.os_exec(rsync_cmd + " --exclude=nest/.git --timeout=120 --progress /var/app/nest "+ host +":/var/app")

            self.os_exec(rsync_cmd + "--exclude=.git --exclude=bin --exclude=obj --timeout=120 --progress " + self.get_source_target_folder() + "/ "+ host + ":" + self.get_source_target_folder() + "/")
            self.os_exec("ssh nest 'deploy'", False)
        except Exception as e:
                print(e)
