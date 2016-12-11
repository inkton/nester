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
     
    id = None
    status = None
    name = None
    first_name = None
    last_name = None
    user_id = None
    email = None
    notify_updates = None   

    def __init__(self, auth, id=None):
        super(Contact, self).__init__(auth)

	self.id = id

        try:
            os.makedirs(self.home + '/contacts')
        except OSError as exception:
	    if exception.errno != errno.EEXIST:
                raise FailedValidation('Unable to create settings directory ' + self.home)

    def new_copy(self, object):
        new_entity = Contact(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser('contacts', help='Manage contacts')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='contact_command', help='Contact commands')

        invite_cmd = app_cmd_parsers.add_parser('invite', help='Invite a contact')    
        invite_cmd.add_argument('-e', '--email', type=str, required=True, help='Email address of the contact')
        app_cmd_parsers.add_parser('list', help='List contacts')    

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == 'contacts':
            self.log("handle contact command")
            cmd_handled = True
            if (args.contact_command == 'invite'):
               self.invite(args.email)
	    elif (args.contact_command == 'list'):
               self.list()
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

    def list(self):
        try:
            self.cache_list("users/{0}/apps/{1}/contacts".format(
		os.environ['NEST_CONTACT_USER_ID'],
		os.environ['NEST_APP_ID']), 
			'contacts', None, 'id')
            self.draw_table("contacts")
	except Exception as e:
            print(e)

    def load(self):
	self.load_object('/contacts/' + str(self.id), self)

    def save(self):
        self.save_object('/contacts/' + str(self.id), self)

    def draw_table_col_width(self, table):
        table.set_cols_width([5, 15, 10, 10, 10, 10, 15])

    def draw_table_col_align(self, table):
        table.set_cols_align(["c", "l", "c", "l", "l", "l", "c"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m", "m", "m", "m", "m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t", "t", "t", "t", "t", "t"])

    def get_table_col_header(self):
        return ["id", "email", "status", "name", "first name", "last name", "notify updates"]

    def get_table_row_data(self, id):
        print_obj = Contact(self.auth, id)
        print_obj.load()
        return [  print_obj.id, print_obj.email, 
		print_obj.status,
		print_obj.name, 
		print_obj.first_name,
		print_obj.last_name, 
		print_obj.notify_updates ]
