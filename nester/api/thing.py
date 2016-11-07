#!/usr/bin/env python
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

class Thing:
    def __init__(self):
        self.apiHost = ''
        self.nestHost = ''

    def init(self, apiHost, nestHost):
        self.apiHost = apiHost
        self.nestHost = nestHost
