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

        app_cmd_parsers.add_parser('pull', help='Download the deployment')
        app_cmd_parsers.add_parser('push', help='Publish the source and deploy')
        app_cmd_parsers.add_parser('restore', help='Restore the project')
        app_cmd_parsers.add_parser('clear', help='Clear the project')
        app_cmd_parsers.add_parser('clean', help='Clean the project')
        app_cmd_parsers.add_parser('build', help='Build the project')
        app_cmd_parsers.add_parser('uncache', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle deployment command")
            cmd_handled = True
            if (args.dep_command == 'pull'):
                self.pull()
            elif (args.dep_command == 'push'):
                self.push()
            elif (args.dep_command == 'restore'):
                self.restore()
            elif (args.dep_command == 'build'):
                self.build()
            elif (args.dep_command == 'clear'):
                self.clear()
            elif (args.dep_command == 'clean'):
                self.clean()
            elif (args.dep_command == 'uncache'):
                self.clear_cache()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def pull_project(self, rsync_cmd, folder, branch):
        self.os_exec("rm -rf " + folder)
        self.os_exec("mkdir -p " + folder)

        self.os_exec(rsync_cmd + " --exclude=.git --exclude=bin --exclude=obj --timeout=600 --progress -e 'ssh' nest:" + folder + "/ " + folder + "/")

        self.os_exec("cd " + folder + " && git init ")
        self.os_exec("cd " + folder + " && git remote add origin nest:repository.git ")
        self.os_exec("cd " + folder + " && git fetch ")
        self.os_exec("cd " + folder + " && git checkout origin/" + branch + " -ft")

    def pull(self):
        try:
            rsync_cmd = "/usr/bin/rsync -avzr "
            self.pull_project(rsync_cmd, self.get_source_target_folder(), self.get_source_target_git_branch())

            if self.get_platform_tag() == "api" or self.get_platform_tag() == "mvc":
                self.pull_project(rsync_cmd, self.get_source_shared_folder(), self.get_source_shared_git_branch())

                self.os_exec(rsync_cmd + " --timeout=600 --progress -e 'ssh' nest:/var/app/log /var/app")
                self.os_exec(rsync_cmd + " --timeout=60 --progress -e 'ssh' nest:/var/app/source/" + self.get_app_tag_capitalized() + ".sln /var/app/source")
                self.os_exec(rsync_cmd + " --timeout=60 --progress -e 'ssh' nest:/var/app/app.nest /var/app")
                self.os_exec(rsync_cmd + " --timeout=60 --progress -e 'ssh' nest:/var/app/app.json /var/app")
                self.os_exec(rsync_cmd + " --exclude=nest/.git --timeout=600 --progress -e 'ssh' nest:/var/app/nest /var/app")
                self.os_exec(rsync_cmd + " --exclude=nest/.git --timeout=600 --progress -e 'ssh' nest:/var/app/downtime /var/app")

            self.setup_git()
        except Exception as e:
                print(e)

    def push(self):
        try:
            rsync_cmd = "/usr/bin/rsync -avzr "
            self.os_exec(rsync_cmd + " --exclude=.git --exclude=bin --exclude=obj --timeout=600 --progress " + self.get_source_shared_folder() + "/ -e 'ssh' nest:" + self.get_source_shared_folder() + "/ ")
            self.os_exec(rsync_cmd + " --timeout=600 --progress /var/app/app.nest -e 'ssh' nest:/var/app")
            self.os_exec(rsync_cmd + " --timeout=600 --progress /var/app/app.json -e 'ssh' nest:/var/app")
            self.os_exec(rsync_cmd + " --exclude=nest/.git --timeout=600 --progress /var/app/nest -e 'ssh' nest:/var/app")
            self.os_exec(rsync_cmd + " --exclude=nest/.git --timeout=600 --progress /var/app/downtime -e 'ssh' nest:/var/app")

            self.os_exec(rsync_cmd + "--exclude=.git --exclude=bin --exclude=obj --timeout=600 --progress " + self.get_source_target_folder() + "/ -e 'ssh' nest:" + self.get_source_target_folder() + "/")
            self.os_exec("ssh nest 'deploy'", False)
        except Exception as e:
                print(e)

    def restore(self):
        self.log("test restore")
        self.os_exec("dotnet restore " + self.get_source_target_source_folder(), False)

    def build(self):
        self.log("build " + self.get_source_target_source_folder())
        self.os_exec("dotnet build " + self.get_source_target_source_folder() + " -c Debug ", False)

    def clean(self):
        self.log("clean")
        self.os_exec("dotnet clean " + self.get_source_target_source_folder())

    def clear(self):
        self.log("remove build folders")
        self.os_exec("rm -rf " + self.get_source_target_source_folder() + "/obj")
        self.os_exec("rm -rf " + self.get_source_target_source_folder() + "/bin")

    def setup_git_for_user(self, user):
        self.log("setup git for user " + user)
        git_config = "sudo su - "+ user +" -c \"git config --file " + self.get_source_target_folder() + "/.git/config "
        self.os_exec(git_config + " user.email "+os.environ['NEST_CONTACT_EMAIL']+ "\"" )
        self.os_exec(git_config + " user.name "+os.environ['NEST_CONTACT_ID']+ "\"" )
        self.os_exec(git_config + " core.autocrlf false\"")
        self.os_exec(git_config + " push.default simple\"")

    def setup_git(self):
        self.log("setup git")
        self.setup_git_for_user(os.environ['NEST_CONTACT_ID'])
