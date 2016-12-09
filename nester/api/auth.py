#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse, requests

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
from daemonize import Daemonize

from nester.api.cloud import Cloud

class Auth(Cloud):
    email = None
    token = None
    password = None
    user = {}
          
    def __init__(self, email, password=None):
        super(Auth, self).__init__(self)

	self.email = email
	self.password = password

        try:
            os.makedirs(self.home + '/auth')
        except OSError as exception:
	    if exception.errno != errno.EEXIST:
                raise FailedValidation('Unable to create settings directory ' + self.home)

    def get_token(self):
        response = requests.get(
          self.get_url('auth/tokens'),
                verify=False,
                params = {'email': self.email,
                        'password' : self.password })

        data = self.get_data(response)
        self.__dict__.update(data)

    def load(self):
	self.load_object('/auth/' + self.email, self)
        return self.password != None

    def save(self):
        self.save_object('/auth/' + self.email, self)

