#!/usr/bin/python
# Copyright (c) 2010(s), Karl S.B. <karl.sundequist.blomdahl@gmail.com>

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from lxml import etree
import Tkinter
import Tix
import sys

class stat:
    def __init__ (self, name, total = 0):
        self.name = name
        self.total = total
        self.summands = []

    def add_summand (self, explain, summand):
        self.summands.append((explain, summand))

    def get_summand (self, explain):
        for (explain_, summand) in self.summands:
            if explain == explain_:
                return summand
        return None

    def update_total (self):
        self.total = 0

        for (explain, summand) in self.summands:
            self.total = self.total + summand

    def format (self):
        return '%s %d' % (self.name.capitalize().replace('_', ' '), self.total)

class item:
    def __init__ (self, tree):
        self.stats = dict()
        self.enchant = []
        self.gems = []
        self.gem_names = []
        self.socket_bonus = []

        self.initialize(tree)

    def __get_stat (self, name):
        if not name in self.stats.keys():
            self.stats[name] = stat(name)
        return self.stats[name]

    def initialize (self, tree):
        self.id = int(tree.xpath('id')[0].text)
        self.name = tree.xpath('name')[0].text

        for s in tree.xpath('base/*'):
            self.__get_stat(s.tag).add_summand('base', int(s.text))

        for gem in tree.xpath('gem'):
            g = []
            for s in gem.xpath('*'):
                self.__get_stat(s.tag).add_summand('gem', int(s.text))
                g.append(stat(s.tag, int(s.text)))
            self.gem_names.append(gem.get('name'))
            self.gems.append(g)

        for s in tree.xpath('reforge/*'):
            self.__get_stat(s.tag).add_summand('reforge', int(s.text))

        for s in tree.xpath('socket_bonus/*'):
            self.__get_stat(s.tag).add_summand('socket bonus', int(s.text))
            self.socket_bonus.append(stat(s.tag, int(s.text)))

        for s in tree.xpath('enchant/*'):
            self.__get_stat(s.tag).add_summand('enchant', int(s.text))
            self.enchant.append(stat(s.tag, int(s.text)))
        if tree.xpath('enchant'):
            self.enchant_name = tree.xpath('enchant')[0].get('name')

        for s in self.stats.values():
            s.update_total()

    def __get_reforged (self):
        plus = None
        minus = None

        for stat in self.stats.values():
            delta = stat.get_summand('reforge')
            if delta and delta > 0:
                plus = stat
            elif delta and delta < 0:
                minus = stat

        if minus and plus:
            return '%s --> %s' % (minus.name.capitalize(),
                                  plus.name.capitalize())
        else:
            return 'False'

    def __get_enchant (self):
        if not self.enchant:
            return 'False'
        return '%s (%s)' % (self.enchant_name, ', '.join(map (lambda x: x.format(), self.enchant)))

    def __get_gem (self, i):
        name = self.gem_names[i]
        gem = self.gems[i]
        if not gem:
            return 'False'
        return '%s (%s)' % (name, ', '.join(map (lambda x: x.format(), gem)))

    def __get_socket_bonus (self):
        if not self.socket_bonus:
            return 'False'
        return ', '.join(map (lambda x: x.format(), self.socket_bonus))

    def add_item (self, hlist):
        self_path = str(self.id)
        reforge_path = '%s.reforge' % (self_path,)
        enchant_path = '%s.enchant' % (self_path,)
        gem_path = '%s.gem' % (self_path,)
        socket_bonus_path = '%s.socket_bonus' % (self_path,)

        hlist.add(self_path, text = self.name)
        hlist.add(reforge_path)
        hlist.item_create(reforge_path, 0, text = 'Reforged')
        hlist.item_create(reforge_path, 1, text = self.__get_reforged())

        hlist.add(enchant_path)
        hlist.item_create(enchant_path, 0, text = 'Enchant')
        hlist.item_create(enchant_path, 1, text = self.__get_enchant())

        for i in range(len(self.gems)):
            gem_path = '%s1' % gem_path

            hlist.add(gem_path)
            hlist.item_create(gem_path, 0, text = 'Gem')
            hlist.item_create(gem_path, 1, text = self.__get_gem(i))

        if self.gems:
            hlist.add(socket_bonus_path)
            hlist.item_create(socket_bonus_path, 0, text = 'Socket Bonus')
            hlist.item_create(socket_bonus_path, 1, text = self.__get_socket_bonus())

class character:
    def __init__ (self, tree):
        self.stats = dict()
        self.items = dict()

        self.initialize(tree)

    def initialize (self, tree):
        for s in tree.xpath('/character/total/*'):
            self.stats[s.tag] = stat(s.tag, int(s.text))
        for s in tree.xpath('/character/base/*'):
            if not s.tag in self.stats.keys():
                self.stats[s.tag] = stat(s.tag, 0)
            self.stats[s.tag].add_summand('base', int(s.text))

        for i in tree.xpath('/character/items/item'):
            item_id = int(i.xpath('id')[0].text)

            self.items[item_id] = item(i)
            for s in self.items[item_id].stats.values():
                self.stats[s.name].add_summand(item_id, s.total)

    def __get_total (self):
        if not self.stats:
            return 'False'
        return ', '.join([ x.format() for x in self.stats.values() ])

    def add_items (self, hlist):
        hlist.add('total')
        hlist.item_create('total', 0, text = 'Total')
        hlist.item_create('total', 1, text = self.__get_total())
        
        for item in self.items.values():
            item.add_item(hlist)

try:
    tree = etree.parse(sys.stdin)
    status = tree.xpath('/character/status')[0].text

    root = Tix.Tk()
    root.title('World of Warcraft Optimizer')

    if status == 'Optimal':
        score = float(tree.xpath('/character/score')[0].text)
        char = character(tree)

        s = Tix.ScrolledHList(root, width = 600, height = 700,
                                    options = 'hlist.columns 2')
        hl = s.hlist
        hl.header_create(0, text = '')
        hl.column_width(0, 150)
        hl.header_create(1, text = '')

        hl.add('score')
        hl.item_create('score', 0, text = 'Score')
        hl.item_create('score', 1, text = '%s' % (score,))

        char.add_items(hl)

        s.pack(expand = True, fill = Tkinter.BOTH)
    else:
        Tix.Message(root, text = "Error: %s" % tree.xpath('/character/message')[0].text).pack(padx = 10, pady = 10)
    root.mainloop()
finally:
    pass
