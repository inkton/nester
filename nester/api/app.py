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

class App(Cloud):

    def __init__(self, auth):
        super(Cloud, self).__init__('app', auth)

    def new_copy(self, object):
        new_entity = App(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage an app')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='app_command', help='App commands')

        app_cmd_parsers.add_parser('attach', help='Attach to the app in the environment')
        app_cmd_parsers.add_parser('test_restore', help='Restore the project for testing')
        app_cmd_parsers.add_parser('test_build', help='Build the project for testing')
        app_cmd_parsers.add_parser('attach', help='Attach to the app in the environment')

        allow_cmd = app_cmd_parsers.add_parser('allow', help='Get update permission to the app')
	allow_cmd.add_argument('-p', '--password', type=str, help='The password')

        app_cmd_parsers.add_parser('revoke', help='Revoke update permission to the app')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
	self.set_log(args.log)

	cmd_handled = False
        if args.command == self.subject:
 	    self.log("handle app command")
            cmd_handled = True
            if (args.app_command == 'attach'):
               self.attach()
            elif (args.app_command == 'test_restore'):
               self.test_restore()
            elif (args.app_command == 'test_build'):
               self.test_build()
            elif (args.app_command == 'allow'):
               self.allow(args.password)
            elif (args.app_command == 'revoke'):
               self.revoke()
            elif (args.app_command == 'clear'):
	       self.clear_cache()
            else:
            	cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def attach(self):
        self.remove_owner()
        self.create_owner()
	host = os.environ['NEST_CONTACT_ID'] + '@' + os.environ['NEST_APP_TAG']+".nestapp.yt"
	rsync_cmd = "/usr/bin/rsync -avzrhe 'ssh -i /var/app/.contact_key -o StrictHostKeyChecking=no' "

        if (os.environ['NEST_PLATFORM_TAG'] != 'worker'):
            self.os_exec(rsync_cmd + " --timeout=60 --progress "+ host +":/var/app/app.nest /var/app")
            self.os_exec(rsync_cmd + " --timeout=60 --progress "+ host +":/var/app/app.json /var/app")
            self.os_exec(rsync_cmd + " --timeout=120 --progress "+ host +":/var/app/nest /var/app")
            self.os_exec(rsync_cmd + " --timeout=120 --progress "+ host +":/var/app/log /var/app")
            self.os_exec(rsync_cmd + " --timeout=120 --progress "+ host +":/var/app/source/shared /var/app/source")
        self.os_exec(rsync_cmd + " --timeout=120 --progress "+ host +":" + self.get_source_target_folder() + " /var/app/source")
        
	self.os_exec("/bin/bash " + self.get_twig_utils_folder() + "/create")
        self.setup_workarea()
        self.setup_git()	
        self.nest_enable_root()

    def allow(self, password):
        try:
            auth = Auth(os.environ['NEST_CONTACT_EMAIL'], password)
            auth.get_token()
            auth.save()
	except Exception as e:
            print(e)

    def revoke(self):
        try:
            auth = Auth(os.environ['NEST_CONTACT_EMAIL'], None)
            auth.save()
	except Exception as e:
            print(e)

    def nest_enable_root(self):
	self.log("enable root to impersonate the nest owner")
        self.os_exec("cp -r /home/"+ os.environ['NEST_CONTACT_ID'] + "/.[a-zA-Z0-9]* /root")
        self.os_exec("chown -R root:root /root/.ssh")
        self.os_exec("chmod 700 /root/.ssh")
        self.os_exec("chmod -R 600 /root/.ssh/*")

    def remove_owner(self):
	self.log("removing current user")
        self.os_exec("userdel --force --remove "+os.environ['NEST_CONTACT_ID'])
        self.os_exec("sed -i /"+os.environ['NEST_CONTACT_ID']+"/d /etc/sudoers.d/99-forest-sudoers")
        self.os_exec("rm -rf /home/"+os.environ['NEST_CONTACT_ID'])
	self.log("removing group")
        self.os_exec("groupdel tree")

    def create_owner(self):
	self.log("add tree group")
        self.os_exec("groupadd --gid 1008 tree")
	self.log("add current user")
        self.os_exec("useradd --uid "+os.environ['NEST_CONTACT_ID']+" --create-home --gid 1008 "+os.environ['NEST_CONTACT_ID'])
        self.os_exec("touch /etc/sudoers.d/99-forest-sudoers")
        self.os_exec("echo '"+os.environ['NEST_CONTACT_ID']+"	ALL=(ALL) NOPASSWD: ALL'  > /etc/sudoers.d/99-forest-sudoers")
        self.os_exec("mkdir /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("echo "+os.environ['NEST_CONTACT_KEY']+" | base64 --decode > /var/app/.contact_key")
        self.os_exec("echo "+os.environ['NEST_TREE_KEY']+" | base64 --decode > /var/app/.tree_key")
	self.os_exec("cp /var/app/.contact_key /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa")
	self.os_exec("cp /var/app/.tree_key /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/known_hosts")
        self.os_exec("chmod -R 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/*")
        self.os_exec("ssh-keygen -f /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa -y > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa.pub")
        self.os_exec("cat /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa.pub > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/authorized_keys")
        self.os_exec("printf 'Host nest\n\tHostName "+os.environ['NEST_APP_TAG']+".nestapp.yt\n\tUser "+os.environ['NEST_CONTACT_ID']+"\n' > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/config")
        self.os_exec("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("chmod 700 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("chmod -R 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/*")

    def setup_workarea(self):
	self.log("setup workarea")
        self.os_exec("echo publish/ > /var/app/.push_excludes")
        self.os_exec("echo publish/ > /var/app/.pull_excludes")
	self.os_exec("rm -rf /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'])
        self.os_exec("mkdir -p /var/app_shadow/source")
        self.os_exec("cp -rs " + self.get_source_target_folder() + " /var/app_shadow/source")
        self.os_exec("cp -rs " + self.get_source_shared_folder() + " /var/app_shadow/source")
        self.os_exec("rm -rf /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'] + "/{bin,obj}" )
        self.os_exec("dotnet restore --packages /var/app/packages /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'], False)
        self.setup_web_statics()

    def setup_web_statics(self):
	self.log("setup webstatic")
        if (os.environ['NEST_PLATFORM_TAG'] != 'worker'):
       	    self.os_exec("rm -rf /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'] + "/wwwroot")
            self.os_exec("rsync -a /var/app/source/" + os.environ['NEST_TAG_CAP'] + "/wwwroot /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'])

    def test_restore(self):
	self.log("test restore")
        self.os_exec("dotnet restore --packages /var/app/packages /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'], False)

    def test_build(self):
	self.log("test build")
	self.os_exec("cp -rs " + self.get_source_target_folder() + " /var/app_shadow/source")
        self.os_exec("cp -rs " + self.get_source_shared_folder() + " /var/app_shadow/source")
	# remove dangling symbolic links
	self.os_exec("find /var/app_shadow/source -xtype l -delete")

        self.os_exec("dotnet clean /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'] )
        self.os_exec("dotnet build /var/app_shadow/source/" + os.environ['NEST_TAG_CAP'] + " -c Debug ", False)
        self.setup_web_statics()

    def setup_git_for_user(self, user):
	self.log("setup git for user " + user)
	git_config = "sudo su - "+ user +" -c \"git config --file " + self.get_source_target_folder() + "/.git/config ";
        self.os_exec(git_config + " user.email "+os.environ['NEST_CONTACT_EMAIL']+ "\"" )
        self.os_exec(git_config + " user.name "+os.environ['NEST_CONTACT_ID']+ "\"" )
        self.os_exec(git_config + " core.autocrlf false\"")
        self.os_exec(git_config + " push.default simple\"")

    def setup_git(self):
	self.log("setup git")
    	self.setup_git_for_user(os.environ['NEST_CONTACT_ID'])


