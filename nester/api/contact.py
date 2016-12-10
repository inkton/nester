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

class Contact(Cloud):
     
    tag = None
    name = None   

    def __init__(self, auth, tag=None):
        super(Contact, self).__init__(auth)

	self.tag = tag

        try:
            os.makedirs(self.home + '/contacts')
        except OSError as exception:
	    if exception.errno != errno.EEXIST:
                raise FailedValidation('Unable to create settings directory ' + self.home)

    def new_copy(self, object):
        new_entity = Tree(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser('contacts', help='Manage contacts')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='contact_command', help='Contact commands')

        list_cmd = app_cmd_parsers.add_parser('invite', help='Invite a contact')    
        list_cmd.add_argument('-e', '--email', type=str, required=True, help='Email address of the contact')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == 'contacts':
            self.log("handle contact command")
            cmd_handled = True
            if (args.contact_command == 'invite'):
               self.invite(args.email)
	    else:
               cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def invite(self, email):
        try:
            self.create("users/{0}/apps/{1}/contacts".format(
		os.environ['NEST_CONTACT_USER_ID'],
		os.environ['NEST_APP_ID']), 
			'contacts', { 'email' : email })
	except Exception as e:
            print(e)

    def list(self, forest_id):
        try:
            self.cache_list("forests/{0}/trees".format(forest_id), 'trees')
            self.draw_table("trees")
	except Exception as e:
            print(e)

    def load(self):
	self.load_object('/trees/' + self.tag, self)

    def save(self):
        self.save_object('/trees/' + self.tag, self)

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


