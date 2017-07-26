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
from domain import Domain

class Certificate(Cloud):
    
    id = None
    tag = None    
    type = None
    app_domain_id = None    
    certificate_chain = None
    private_key = None

    def __init__(self, auth, tag=None):
        super(Certificate, self).__init__('certificates', auth)
	self.tag = tag

    def new_copy(self, object):
        new_entity = Certificate(self.auth) 
	new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage certificates')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='cert_command', help='Certificate commands')

        sub_cmd = app_cmd_parsers.add_parser('add', help='Add certificate')
        sub_cmd.add_argument('-d', '--domain-tag', type=str, required=True, help='Tag of the domain')
        sub_cmd.add_argument('-t', '--tag', type=str, required=True, help='A memorable identifier. Must be lower case without spaces')
        sub_cmd.add_argument('-y', '--type', choices=['free','custom'], required=True, help='Certificate type')
        sub_cmd.add_argument('-c', '--cert-chain-file', type=str, required=False, help='File containing certificate chain')
        sub_cmd.add_argument('-k', '--cert-key-file', type=str, required=False, help='File containing certificate key')
        
	sub_cmd = app_cmd_parsers.add_parser('remove', help='Remove certiicate')
        sub_cmd.add_argument('-d', '--domain-tag', type=str, required=True, help='Tag of the domain')
        sub_cmd.add_argument('-t', '--tag', type=str, required=True, help='A certificate tag')
        
        sub_cmd = app_cmd_parsers.add_parser('list', help='List all certificates')
        sub_cmd.add_argument('-d', '--domain-tag', type=str, required=True, help='Tag of the domain')
          
        app_cmd_parsers.add_parser('clear', help='Clear cache')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle cert command")
            cmd_handled = True
            if (args.cert_command == 'add'):
               self.add(args.domain_tag, args.tag, args.type, 
		args.cert_chain_file, args.cert_key_file)
            elif (args.cert_command == 'remove'):
               self.remove(args.domain_tag, args.tag)
            elif (args.cert_command == 'list'):
               self.list(args.domain_tag)
            elif (args.cert_command == 'clear'):
	       self.clear_cache()
            else:
                cmd_handled = False
            self.end_cmd()
        return cmd_handled
 
    def get_parent_domain(self, domain_tag):
        domain = Domain(self.auth, domain_tag)
	domain.cache_list("apps/{0}/domains".format(
            os.environ['NEST_APP_ID']), 
            None, 'tag')
        if not domain.load():
            print "the domain does not exist"
            return None
        return domain

    def add(self, domain_tag, tag, type, 
		cert_chain_file, cert_key_file):
        try: 
            owned_by_obj = self.get_parent_domain(domain_tag)
	    if owned_by_obj is None:
               return

            cert_chain=None
            cert_key=None

            if type == 'custom':
                with open(cert_chain_file, 'r') as chain_file:
                    cert_chain=chain_file.read().replace('\n', '')
                if len(cert_chain) < 32:
                    print "Certification chain file seems corrupt"
                    return

                with open(cert_key_file, 'r') as key_file:
                    cert_key=key_file.read().replace('\n', '')
                if len(cert_key) < 32:
                    print "Certification key file seems corrupt"
                    return
 
            self.create("apps/{0}/domains/{1}/certificates".format(
		os.environ['NEST_APP_ID'],
		owned_by_obj.id 
		), 
		{
		'tag' : tag, 
		'type' : type,
		'certificate_chain' : cert_chain,
		'certificate_chain' : cert_key
		}
	    )

	except Exception as e:
            print(e)

    def remove(self, domain_tag, tag):
        try:
            owned_by_obj = self.get_parent_domain(domain_tag)
	    if owned_by_obj is None:
               return

            self.cache_list("apps/{0}/domains/{1}/certificates".format(
		os.environ['NEST_APP_ID'],
		owned_by_obj.id 
		), None, 'tag')

	    remove_obj = Certificate(self.auth, tag)
            if not remove_obj.load():
               print "the domain certificate does not exist"
               return

            if (self.confirm("Are you sure to remove the certificate " + tag +
		" ?\n", default="no")) :
		self.delete("apps/{0}/domains/{1}/certificates/{2}".format(
		  os.environ['NEST_APP_ID'],
		  owned_by_obj.id, remove_obj.id), {})

	except Exception as e:
            print(e)

    def list(self, domain_tag):
	self.log("cert list")
        try:
            owned_by_obj = self.get_parent_domain(domain_tag)
	    if owned_by_obj is None:
               return

            self.cache_list("apps/{0}/domains/{1}/certificates".format(
		os.environ['NEST_APP_ID'],
		owned_by_obj.id 
		), 
		None, 'tag')

            self.draw_table()
	except Exception as e:
            print(e)

    def load(self):
	return self.load_by_key(self.tag)

    def save(self):
        return self.save_by_key(self.tag)

    def draw_table_col_width(self, table):
        table.set_cols_width([5, 10, 8, 10])

    def draw_table_col_align(self, table):
        table.set_cols_align(["c", "r", "r", "r"])

    def draw_table_col_valign(self, table):
        table.set_cols_align(["m", "m", "m", "m"])

    def draw_table_col_dtype(self, table):
        table.set_cols_align(["t", "t", "t", "t"])

    def get_table_col_header(self):
        return ["id", "tag", "type", "domain_id" ]

    def get_table_row_data(self, tag):
        print_obj = Certificate(self.auth, tag)
        print_obj.load()
        return [  print_obj.id, print_obj.tag, 
		print_obj.type, 
		print_obj.app_domain_id ]

