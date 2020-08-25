##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2013-2016 Uwe Hermann <uwe@hermann-uwe.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd
from common.srdhelper import bitpack

'''
OUTPUT_PYTHON format:

Packet:
[<ptype>, <pdata>]

<ptype>, <pdata>
 - 'ITEM', [<item>, <itembitsize>]
 - 'WORD', [<word>, <wordbitsize>, <worditemcount>]

<item>:
 - A single item (a number). It can be of arbitrary size. The max. number
   of bits in this item is specified in <itembitsize>.

<itembitsize>:
 - The size of an item (in bits). For a 4-bit parallel bus this is 4,
   for a 16-bit parallel bus this is 16, and so on.

<word>:
 - A single word (a number). It can be of arbitrary size. The max. number
   of bits in this word is specified in <wordbitsize>. The (exact) number
   of items in this word is specified in <worditemcount>.

<wordbitsize>:
 - The size of a word (in bits). For a 2-item word with 8-bit items
   <wordbitsize> is 16, for a 3-item word with 4-bit items <wordbitsize>
   is 12, and so on.

<worditemcount>:
 - The size of a word (in number of items). For a 4-item word (no matter
   how many bits each item consists of) <worditemcount> is 4, for a 7-item
   word <worditemcount> is 7, and so on.
'''

def channel_list(num_channels):
    l = [{'id': 'rs', 'name': 'RS', 'desc': 'Read Strobe'},
         {'id': 'ws', 'name': 'WS', 'desc': 'Write Strobe'}]
    for i in range(6):
        a = {'id': 'a%d' % i, 'name': 'A%d' % i, 'desc': 'Address line %d' % i}
        l.append(a)
    for i in range(8):
        d = {'id': 'd%d' % i, 'name': 'D%d' % i, 'desc': 'Data line %d' % i}
        l.append(d)
    return tuple(l)

class ChannelError(Exception):
    pass

NUM_CHANNELS = 8

class Decoder(srd.Decoder):
    api_version = 3
    id = 'async'
    name = 'Async'
    longname = 'Async Parallel bus'
    desc = 'SRAM-like async parallel bus.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['async']
    tags = ['Util']
    channels = channel_list(NUM_CHANNELS)
    options = (
        {'id': 'strobe_pol', 'desc': 'Strobe Polarity',
            'default': 'active_low', 'values': ('active_low', 'active_high')},
    )
    annotations = (
        ('item', 'Item'),
        ('warn', 'Word'),
    )
    annotation_rows = (
        ('items', 'Items', (0,)),
        ('warns', 'Warnings', (1,)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.ss_item = self.es_item = None

    def start(self):
        self.out_python = self.register(srd.OUTPUT_PYTHON)
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def putpb(self, data):
        self.put(self.ss_item, self.es_item, self.out_python, data)

    def putb(self, data):
        self.put(self.ss_item, self.es_item, self.out_ann, data)

    def decode(self):
        self.fmt_item = "{} {:02x} : {:02x}"

        # Keep processing the input stream. Assume "always zero" for
        # not-connected input lines. Pass data bits (all inputs except
        # clock) to the handle_bits() method.
        while True:
            pins = self.wait([{0: 'f'},{1: 'f'}])
            self.ss_item = self.samplenum
            if not pins[0]:
                addr = pins[2:8] #gah. Python indexing will never not be wrong
                pins = self.wait({0:'r'})
                self.es_item = self.samplenum
                data = pins[8:16]
                self.putpb(['ITEM', pins])
                addr = bitpack(addr)
                print(data)
                data = bitpack(data)
                print(data)
                self.putb([0, [self.fmt_item.format('R',addr,data)]])
            elif not pins[1]:
                addr = pins[2:8]
                data = pins[8:16]
                pins = self.wait({1:'r'})
                self.es_item = self.samplenum
                addr = bitpack(addr)
                data = bitpack(data)
                self.putpb(['ITEM', pins])
                self.putb([0, [self.fmt_item.format('W',addr,data)]])
