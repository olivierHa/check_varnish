#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Website : https://github.com/olivierHa/check_varnish
# Copyright (C) 2015 : Olivier Hanesse olivier.hanesse@gmail.com
# Modifications (C) 2017 : Claudio Kuenzler www.claudiokuenzler.com

"""Varnish Nagios check."""

import nagiosplugin

import sys
import argparse
import subprocess
import json

class Varnish(nagiosplugin.Resource):

    def __init__(self, field):
      self.field = args.arg_field

    def probe(self):
      try:
        if args.arg_name:
          cmd = ['/usr/bin/varnishstat','-1','-j','-n', args.arg_name]
        else:
          cmd = ['/usr/bin/varnishstat','-1','-j']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, unused_err = process.communicate()
        retcode = process.poll()
      except OSError, e:
        print "Error: Executing command failed,  does it exist?"
        sys.exit(2)

      json_data = json.loads(output)
      value = json_data[self.field]['value']
      return [nagiosplugin.Metric(self.field, value, context='varnish')]


def main():
    check = nagiosplugin.Check(Varnish())
    check.main()

if __name__ == '__main__':
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-w', '--warning', metavar='RANGE', default='',
                      help='return warning if value is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='',
                      help='return critical if value is outside RANGE')
    argp.add_argument('-f', '--field', metavar='FIELD', dest='arg_field', required=True, action='store', default='MAIN.sess_dropped',
                      help='field to query')
    argp.add_argument('-n', '--name', metavar='NAME', dest='arg_name', action='store', default='',
                      help='name of Varnish instance (optional)')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        Varnish(args.arg_field),
        nagiosplugin.ScalarContext('varnish', args.warning, args.critical))
    check.main()
