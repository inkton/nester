#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse, json
import re

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
import re
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
        app_cmd_parsers.add_parser('push', help='Push the source to the remote')
        app_cmd_parsers.add_parser('deploy', help='Remote build and deploy')
        app_cmd_parsers.add_parser('restore', help='Restore the project')
        app_cmd_parsers.add_parser('clear', help='Clear the project')
        app_cmd_parsers.add_parser('clean', help='Clean the project')
        app_cmd_parsers.add_parser('build', help='Build the project')
        app_cmd_parsers.add_parser('clean_build_tests', help='Clean build unit tests')
        app_cmd_parsers.add_parser('unit_test_debug_host', help='Spawn unit test debug')
        app_cmd_parsers.add_parser('restore_all', help='Restore all projects')
        app_cmd_parsers.add_parser('release_clean_all', help='Release clean all')
        app_cmd_parsers.add_parser('release_build_all', help='Release build all')
        app_cmd_parsers.add_parser('release_test_all', help='Release test all')
        app_cmd_parsers.add_parser('release_coverage_report', help='Release produce report')
        app_cmd_parsers.add_parser('release_upload_all', help='Release upload all')
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
            elif (args.dep_command == 'deploy'):
                self.deploy()
            elif (args.dep_command == 'restore'):
                self.restore()
            elif (args.dep_command == 'build'):
                self.build()
            elif (args.dep_command == 'clear'):
                self.clear()
            elif (args.dep_command == 'clean_build_tests'):
                self.clean_build_debug_tests()
            elif (args.dep_command == 'unit_test_debug_host'):
                self.unit_test_debug_host()
            elif (args.dep_command == 'restore_all'):
                self.restore_all()
            elif (args.dep_command == 'release_clean_all'):
                self.release_clean_all()
            elif (args.dep_command == 'release_build_all'):
                self.release_build_all()
            elif (args.dep_command == 'release_test_all'):
                self.release_test_all()
            elif (args.dep_command == 'release_coverage_report'):
                self.release_coverage_report()
            elif (args.dep_command == 'release_upload_all'):
                self.release_upload_all()
            elif (args.dep_command == 'clean'):
                self.clean()
            elif (args.dep_command == 'uncache'):
                self.clear_cache()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def pull(self):
        try:
            self.os_exec("mkdir " + self.get_source_folder())
            
            self.os_exec(self.transfer_cmd() + "nest:" + self.get_source_target_folder() + "/ " + self.get_source_target_folder() + "/")
            self.os_exec(self.transfer_cmd() + "nest:" + self.get_source_shared_folder() + "/ " + self.get_source_shared_folder() + "/")

            self.os_exec(self.transfer_cmd() + "nest:/var/app/log /var/app", False)

            self.os_exec(self.transfer_cmd() + "nest:/var/app/source/" + self.get_app_tag_capitalized() + ".sln /var/app/source", False)
            self.os_exec(self.transfer_cmd() + "nest:/var/app/app.nest /var/app", False)
            self.os_exec(self.transfer_cmd() + "nest:/var/app/app.json /var/app", False)
            self.os_exec(self.transfer_cmd() + "nest:/var/app/nest /var/app", False)
            self.os_exec(self.transfer_cmd() + "nest:/var/app/downtime /var/app", False)

            self.setup_git()
        except Exception as e:
            print(e)

    def push(self):
        try:
            self.os_exec(self.transfer_cmd() + "/var/app/source nest:/var/app/source/" + self.get_app_tag_capitalized() + ".sln", False)
            self.os_exec(self.transfer_cmd() + "/var/app/app.nest nest:/var/app", False)
            self.os_exec(self.transfer_cmd() + "/var/app/app.json nest:/var/app", False)
            self.os_exec(self.transfer_cmd() + "/var/app/nest nest:/var/app", False)
            self.os_exec(self.transfer_cmd() + "/var/app/downtime nest:/var/app", False)

            self.os_exec(self.transfer_cmd() + self.get_source_shared_folder() + "/  nest:" + self.get_source_shared_folder() + "/", False)
            self.os_exec(self.transfer_cmd() + self.get_source_target_folder() + "/ nest:" + self.get_source_target_folder() + "/", False)
        except Exception as e:
            print(e)

    def deploy(self):
        try:
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
        self.os_exec("dotnet clean " + self.get_source_target_source_folder(), False)

    def clear(self):
        self.log("remove build folders")
        self.os_exec("rm -rf " + self.get_source_target_source_folder() + "/obj", False)
        self.os_exec("rm -rf " + self.get_source_target_source_folder() + "/bin", False)

    def clean_build_debug_tests(self):
        self.log("build debug tests")
        self.os_exec("rm -rf " + self.get_source_target_test_folder() + "/obj")
        self.os_exec("rm -rf " + self.get_source_target_test_folder() + "/bin")
        self.os_exec("dotnet build " + self.get_source_target_test_folder() + " -c Debug ", False)

    def unit_test_debug_host(self):
        self.os_exec("pkill dotnet")
        # do the UNIX double-fork magic, see Stevens' "Advanced 
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        # https://stackoverflow.com/questions/6011235/run-a-program-from-
        # python-and-have-it-continue-to-run-after-the-script-is-kille
        try: 
            pid = os.fork() 
            if pid > 0:
                # parent process, return and keep running
                return
        except OSError, e:
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1)
        os.setsid()
        # do stuff
        my_env = os.environ.copy()
        my_env["VSTEST_HOST_DEBUG"] = "1"
        devnull = open(os.devnull, 'wb')
        proc = Popen(["/usr/bin/dotnet", "exec", self.get_vtest_console_runtime_path(), 
            self.get_source_target_test_runtime_path()], stdout=PIPE, env=my_env)
        bite_this = re.compile("Process Id:+\s+(\d*), Name:+\sdotnet")
        while proc.poll() is None:
            out = proc.stdout.readline()
            match = bite_this.search(out)
            if match:
                print match.group(1)
                break
        # all done
        os._exit(os.EX_OK)

    def setup_git_folder(self, folder):
        self.log("setup git folder " + folder)
        git_command = "git -C " + folder + " "        
        self.os_exec(git_command + "init")
        self.os_exec(git_command + "config --file "+ folder + "/.git/config user.email "+os.environ['NEST_CONTACT_EMAIL'] )
        self.os_exec(git_command + "config --file "+ folder + "/.git/config user.name "+os.environ['NEST_CONTACT_ID'] )        
        self.os_exec(git_command + "remote rm origin ")
        self.os_exec(git_command + "remote add origin nest:repository.git ")
        self.os_exec(git_command + "fetch origin --tags")

    def setup_git(self):
        self.log("setup git")
        self.os_exec("git config --global user.email "+os.environ['NEST_CONTACT_EMAIL'] )
        self.os_exec("git config --global user.name "+os.environ['NEST_CONTACT_ID'] )        
        self.setup_git_folder(self.get_source_shared_folder())
        self.setup_git_folder(self.get_source_target_folder())

    def apply_all_projects(self, op, command, test_only):
        self.log("restore all with settings " + self.get_app_folder() + "/settings.json")
        with open(self.get_app_folder() + "/settings.json") as settings_file:
            settings = json.load(settings_file)            
            machine = "app-" + settings["app"]["environment"]["NEST_TAG"]
            target_folder = settings["app"]["environment"]["NEST_FOLDER_SOURCE"] + '/' + settings["app"]["environment"]["NEST_TAG_CAP"]
            title = op + " the app " + settings["app"]["environment"]["NEST_TAG_CAP"]
            print title
            print '-' * len(title)
            if not test_only:
                self.os_exec(self.remote_shell_cmd() + machine + " " + command + " " + target_folder +"/src", False, True)
            self.os_exec(self.remote_shell_cmd() + machine + " " + command + " " + target_folder +"/test", False, True)
            i = 0
            while i < len(settings["workers"]):
                machine = "worker-" + settings["workers"][i]["environment"]["NEST_TAG"]
                target_folder = settings["workers"][i]["environment"]["NEST_FOLDER_SOURCE"] + '/' + settings["workers"][i]["environment"]["NEST_TAG_CAP"]
                title = "\n" + op + " the worker " +settings["workers"][i]["environment"]["NEST_TAG_CAP"]
                print title
                print '-' * len(title)
                if not test_only:
                    self.os_exec(self.remote_shell_cmd() + machine + " " + command + " " + target_folder +"/src", False, True)
                self.os_exec(self.remote_shell_cmd() + machine + " " + command + " " + target_folder +"/test", False, True)
                i += 1

    def restore_all(self):
        try:        
            self.log("restore all")
            self.apply_all_projects("Restoring", "dotnet restore", False)
        except Exception as e:
            print '-- Ended --'
            sys.exit(-1)
            
    def release_build_all(self):
        try:
            self.log("release build all")
            self.apply_all_projects("Restoring", "dotnet build --configuration Release --output " + self.get_publish_folder(), False)
        except Exception as e:
            print '-- Ended --'
            sys.exit(-1)

    def release_clean_all(self):
        try:
            self.log("release clean all")
            self.apply_all_projects("Clean", "dotnet clean --configuration Release ", False)
        except Exception as e:
            print '-- Ended --'
            sys.exit(-1)

    def release_test_all(self):
        try:
            self.log("release test all")
            self.apply_all_projects("Testing", "dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=cobertura --configuration Release --output " + self.get_publish_folder(), True)
        except Exception as e:
            print '-- Ended --'
            sys.exit(-1)

    def release_coverage_report(self):
        try:
            with open(self.get_app_folder() + "/settings.json") as settings_file:
                settings = json.load(settings_file)            
                machine = "app-" + settings["app"]["environment"]["NEST_TAG"]
                command = "/root/.dotnet/tools/reportgenerator -reports:$NEST_FOLDER_SOURCE/*/*/coverage.cobertura.xml -targetdir:$NEST_FOLDER_PUBLISH/reports"
                self.os_exec(self.remote_shell_cmd() + machine + " " + command, False)
        except Exception as e:
            print '-- Ended --'
            sys.exit(-1)

    def release_upload_all(self):
        try:
            self.log("release deploy all")
            print "Uploading app assets"
            print "--------------------"
            self.os_exec(self.transfer_cmd() + " /var/app/app.nest nest:/var/app", False, True)
            self.os_exec(self.transfer_cmd() + " /var/app/app.json nest:/var/app", False, True)
            self.os_exec(self.transfer_cmd() + " /var/app/nest nest:/var/app", False, True)
            self.os_exec(self.transfer_cmd() + " /var/app/downtime/ nest:/var/app/downtime/", False, True)
            print "\nUploading the app source code"
            print "------------------------------"
            self.os_exec(self.transfer_cmd() + " /var/app/source/ nest:/var/app/source/", False, True)
        except Exception as e:
            print '-- Ended --'
            sys.exit(-1)
