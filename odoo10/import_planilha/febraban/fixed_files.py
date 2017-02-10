# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals
import json
from collections import namedtuple
#from Exceptions import FieldLengthOverflow
from odoo.addons.import_planilha.febraban.Exceptions import FieldLengthOverflow

__author__ = 'flavio@casacurta.com'

class Fixed_files(object):


    def __init__(self, filejson, dic=False, checklength=False):

        self.dic = dic
        self.checklength = checklength

        try:
            if filejson.endswith('.json'):
                attrs = open(filejson).readlines()
            else:
                attrs = open('{}.json'.format(filejson)).readlines()
        except:
            attrs = []

        self.lattrs = [json.loads(line.decode('utf-8')) for line in attrs]

        self.attr = [att['field'] for att in self.lattrs]

        start = 0
        for att in self.lattrs:
            exec ("self.{} = slice({}, {})".format(att['field'], start, (start + int(att['length']))))
            start += int(att['length'])

        self.slices = ''
        for att in self.lattrs:
            if att['type'] == 'str':
                self.slices += 'record[self.{}], '.format(att['field'])
            elif att['type'] == 'int':
                if int(att['decimals']):
                    self.slices += 'round('
                self.slices += 'int(record[self.{}])'.format(att['field'])
                if int(att['decimals']):
                    self.slices += ' * .{0:>0{1}}, {1})'.format('1', att['decimals'])
                self.slices += ', '

        fmt_out_str = ''
        fmt_out_fmt = ''
        for att in self.lattrs:
            if att['type'] == 'str':
                fmt_out_str += "{}".format('{:<' + att['length'] + '}')
                if self.dic:
                    fmt_out_fmt += 'record["{}"][:{}], '.format(att['field'], att['length'])
                else:
                    fmt_out_fmt += 'record.{}[:{}], '.format(att['field'], att['length'])
            elif att['type'] == 'int':
                if int(att['decimals']):
                    dec = ' * {}'.format(int('{:<0{}}'.format('1', int(att['decimals'])+1)))
                else:
                    dec = ''
                fmt_out_str += '{}'.format('{:>0' + att['length'] + '}')
                if self.dic:
                    fmt_out_fmt += 'str(int(record["{}"]{}))[:{}]'.format(att['field'], dec, att['length'])
                else:
                    fmt_out_fmt += 'str(int(record.{}{}))[:{}]'.format(att['field'], dec, att['length'])
                fmt_out_fmt += ', '
        self.fmt_out = "'" + fmt_out_str + "\\n'.format(" + fmt_out_fmt + ")"
        self.Record = namedtuple('Record', self.attr)


    def parse(self, record):

        nt = eval("self.Record({})".format(self.slices))

        if self.dic:
#           return dict(nt._asdict())
            return {k:nt[n] for n, k in enumerate(self.attr)}
            '''
            >>> %timeit -n100000 dict(nt._asdict())
            100000 loops, best of 3: 14.1 microseconds per loop
            >>> %timeit -n100000 {k:nt[n] for n, k in enumerate(ff.attr)}
            100000 loops, best of 3: 909 nanoseconds per loop
            1 microsecond = 1.000 nanoseconds
            14.1*1000/909
            15.51 fast
            '''
        else:
            return nt


    def unparse(self, record):

        if self.checklength:
            for att in self.lattrs:
                if att['type'] == 'str':
                    if self.dic:
                        check = 'len(record["{}"]) > {}'.format(att['field'], att['length'])
                    else:
                        check = 'len(record.{}) > {}'.format(att['field'], att['length'])
                elif att['type'] == 'int':
                    if int(att['decimals']):
                        dec = ' * {}'.format(int('{:<0{}}'.format('1', int(att['decimals'])+1)))
                    else:
                        dec = ''
                    if self.dic:
                        check = 'len(str(int(record["{}"]{}))) > {}'.format(att['field'], dec, att['length'])
                    else:
                        check = 'len(str(int(record.{}{}))) > {}'.format(att['field'], dec, att['length'])
                if eval(check):
                    raise FieldLengthOverflow

        return eval("{}".format(self.fmt_out))

