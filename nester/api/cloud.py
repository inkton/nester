#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>

#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys, logging
from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
import requests, httplib, jsonpickle
import argparse, abc

from nester.api.thing import Thing, FailedValidation

class Cloud(Thing):
    protocol = 'https://'
    host = 'api.nest.yt'
    base_uri = '/'
    logfile = None
    auth = None

    def __init__(self, subject, auth):
        super(Cloud, self).__init__(subject)
        self.auth = auth
        #self.enable_logging()
        requests.packages.urllib3.disable_warnings()

    @abc.abstractmethod
    def new_copy(self, object):
        return None

    def get_url(self, uri):
        return self.protocol + self.host + self.base_uri + uri

    def enable_logging(self):
        httplib.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def create(self, url, data={}):
        filter = {}
        filter['token'] = self.auth.token
        self.clear_cache()
        response = requests.post(
           self.get_url(url), json=data, 
		verify = False, params = filter)
        return self.get_data(response)

    def update(self, url, data={}):
        filter = {}
        filter['token'] = self.auth.token
        self.clear_cache()
        response = requests.put(
           self.get_url(url), json=data, 
		verify = False, params = filter)
        return self.get_data(response)

    def delete(self, url, data={}):
        filter = {}
        filter['token'] = self.auth.token
        self.clear_cache()
        response = requests.delete(
           self.get_url(url), json=data, 
		verify = False, params = filter)

    def query(self, url, filter=None):
        if filter is None:
            filter = {}
        filter['token'] = self.auth.token
        response = requests.get(
          self.get_url(url),
                verify = False,
                params = filter)
        return self.get_data(response)

    def cache_list(self, url=None, filter=None, key='tag'):
	if url is None:
            url = self.subject
	if len(os.listdir(self.get_folder())):
           return False
	return self.query_list(url, filter, key)

    def query_list(self, url=None, filter=None, key='tag'):
	if url is None:
            url = self.subject
        self.clear_cache()
        data = self.query(url, filter)
        list = data[self.subject]
	for object in list:
            create_entity = self.new_copy(object)
            create_entity.save_by_key(str(eval('create_entity.%s' % key)))
        return True

    def get_data(self, response):
        if response.status_code == 401 :
            raise FailedValidation('Not Authorised.')
        elif response.status_code == 500 :
            raise FailedValidation('Fatal error - please notify admin.')
        elif response.status_code == 200:
            result = response.json()
            if result['result_code'] == 0:
                return result['data'] 
            else:
                raise FailedValidation(result['result_text'])

