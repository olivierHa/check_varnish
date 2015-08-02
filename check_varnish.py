#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Website : https://github.com/olivierHa/check_varnish
# Copyright (C) 2015 : Olivier Hanesse olivier.hanesse@gmail.com

"""Varnish Nagios check."""

import nagiosplugin

import sys
import argparse
import subprocess
import json

class Varnish(nagiosplugin.Resource):

    def __init__(self, field):
      self.field = field


    def probe(self):
      try:
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
    argp.add_argument('-f', '--field', metavar='FIELD', action='store', default='MAIN.sess_dropped',
                      help='field to query')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        Varnish(args.field),
        nagiosplugin.ScalarContext('varnish', args.warning, args.critical))
    check.main()

