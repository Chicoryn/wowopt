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
import StringIO
import json
import math
import pulp
import pycurl
import random
import sys
import optparse

''' Stat array indices '''
I = dict({ 'strength': 0,
           'intellect': 1,
           'agility': 2,
           'stamina': 3,
           'resilience': 4,
           'hps': 5,
           'spirit': 6,
           'haste': 7,
           'mastery': 8,
           'critical': 9,
           'hit': 10,
           'expertise': 11,
           'parry': 12,
           'mana': 13,
           'dodge': 14,
           'spell penetration': 15,
           'spell power': 16,
           'damage': 17,
           'attack power': 18,
           'block': 19,
           'armor': 20,
           'dps': 21,
           'ranged attack power': 22 })

''' Gem colour '''
G = dict({ 'red': 1,
           'blue': 2,
           'yellow': 4,
           'purple': 3,
           'orange': 5,
           'green': 6,
           'prismatic': 7 })

def fmt_stats (stat):
    global I

    results = []
    stat_name = dict()

    for k in I.keys():
        stat_name[I[k]] = k.replace(' ', '_')

    for i in range(len(stat)):
        if stat[i] != 0:
            assert (i in stat_name.keys())

            results.append('<%s><![CDATA[%d]]></%s>' % (stat_name[i], int(stat[i]), stat_name[i]))

    return '\n'.join(results)

def make_stats (stat = {}, default = lambda x: 0):
    global I

    results = []
    for k in range(max(I.values())+1):
        results.append(default(k))

    for k in stat.keys():
        if type(k) == str:
            assert (k.lower() in I.keys())

            results[I[k.lower()]] = stat[k]
        else:
            results[k] = stat[k]

    return results

class socket:
    def __init__ (self, colour):
        global G

        if type(colour) is str:
            self.colour = G[colour.lower()]
        else:
            self.colour = colour

    def matches (self, gem):
        return (gem.colour & self.colour) > 0

class armory_base:
    equipT = { 'agility': 'agi',
               'intellect': 'int',
               'spirit': 'spi',
               'stamina': 'sta',
               'strength': 'str',
               'haste': 'hastertng',
               'mastery': 'mastrtng',
               'spell power': 'splpwr',
               'critical': 'critstrkrtng',
               'hit': 'hitrtng',
               'attack power': 'atkpwr',
               'ranged attack power': 'rgdatkpwr',
               'expertise': 'exprtng',
               'dodge': 'dodgertng',
               'block': 'blockrtng',
               'parry': 'parryrtng',
               'resilience': 'resirtng',
               'spell penetration': 'splpen',
               'mana': 'mana',
               'damage': 'damage' }

    def __init__ (self):
        pass

    def load_doc (self, url, cache = None):
        body = StringIO.StringIO()

        if cache:
            try:
                with open(cache, 'r') as fd:
                    body.write(fd.read())
                fd.close()

                return body.getvalue()
            except IOError as e:
                pass

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, [ 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4',
                                 'Content-Type: text/xml' ])
        c.setopt(c.WRITEFUNCTION, body.write)

        if cache:
            try:
                io_error = False
                fd = open(cache, 'w')

                def cache_write (buf):
                    if not io_error:
                        fd.write(buf)
                    return body.write(buf)

                c.setopt(c.WRITEFUNCTION, cache_write)
            except IOError as e:
                io_error = True

        c.perform()
        c.close()

        if cache and not io_error:
            fd.close()

        return body.getvalue()

class gem (armory_base):
    def __init__ (self, item_id):
        global G

        doc = self.load_doc('www.wowhead.com/item=%d&xml' % item_id,
                            cache = 'cache/%d.xml' % item_id)
        tree = etree.XML(doc)

        if not tree.xpath('/wowhead/item'):
            raise Exception('No such gem %d' % item_id)

        wowhead_json = tree.xpath('/wowhead/item/json')[0].text
        wowhead_jsonEquip = tree.xpath('/wowhead/item/jsonEquip')[0].text

        info = json.loads('{' + wowhead_json + '}')
        equip = json.loads('{' + wowhead_jsonEquip + '}')

        colourT = dict({ 0: G['red'],
                         1: G['blue'],
                         2: G['yellow'],
                         3: G['purple'],
                         4: G['green'],
                         5: G['orange'],
                         8: G['prismatic'] })

        self.name = info['name'][1:]
        self.id = item_id
        if not info['classs'] == 3:
            raise Exception('%s (%d): is not a gem' % (self.name, item_id))
        self.stats = dict()
        for a in self.equipT.keys():
            if self.equipT[a] in equip.keys():
                self.stats[a] = equip[self.equipT[a]]
        self.stats = make_stats(self.stats)
        self.colour = colourT[info['subclass']]

class enchant (armory_base):
    def __init__ (self, item_id):
        doc = self.load_doc('www.wowhead.com/item=%d&xml' % item_id,
                            cache = 'cache/%d.xml' % item_id)
        tree = etree.XML(doc)

        if not tree.xpath('/wowhead/item'):
            raise Exception('%d: No such item' % item_id)
        if not tree.xpath('/wowhead/item/jsonUse'):
            raise Exception('%d: Not an usable item' % item_id)

        wowhead_json = tree.xpath('/wowhead/item/json')[0].text
        wowhead_jsonUse = tree.xpath('/wowhead/item/jsonUse')[0].text

        info = json.loads('{' + wowhead_json + '}')
        use = json.loads('{' + wowhead_jsonUse + '}')

        self.name = info['name'][1:]
        self.id = item_id

        if not (info['classs'] == 0 and info['subclass'] == 6):
            raise Exception('%s (%d): Not an enchant' % (self.name, item_id))

        stats = dict()
        for a in self.equipT.keys():
            if self.equipT[a] in use.keys():
                stats[a] = use[self.equipT[a]]
        self.stats = make_stats(stats)

class armory_character (armory_base):
    def __init__ (self):
        pass

    def load_character (self, name, realm, region):
        doc = self.load_doc('www.rawr4.com/%s@%s-%s' % (name, region, realm))
        tree = etree.XML(doc)

        slots = [ 'Head', 'Neck', 'Shoulders', 'Back', 'Chest', 'Hands', 'Waist', 'Wrist', 'Legs', 'Feet', 'Finger1', 'Finger2', 'Trinket1', 'Trinket2', 'MainHand', 'OffHand', 'Ranged' ]

        for slot in slots:
            for code in tree.xpath(slot):
                self.item_ids.append(int(code.text.split('.')[0]))

class xml_character:
    def __init__ (self):
        pass

    def __c (self, text):
        return text.replace('_', ' ')

    def load_character (self, fd):
        tree = etree.parse(fd)
        info = tree.xpath('/character/info')

        if not info:
            raise Exception('Incorrectly formatted character file')
        else:
            info = info[0]

        self.is_loaded = info.get('load', default = 'false').lower() == 'false'

        if not self.is_loaded:
            self.name = info.xpath('name')[0].text
            self.realm = info.xpath('realm')[0].text
            self.region = info.xpath('region')[0].text

        base_stats = {}
        for stat in info.xpath('base/*'):
            base_stats[self.__c(stat.tag)] = int(stat.text)
        self.base_stats = make_stats(base_stats)

        weight = {}
        for stat in tree.xpath('/character/weights/*'):
            weight[self.__c(stat.tag)] = float(stat.text)
        self.weight = make_stats(weight, lambda x: 0)

        self.additional_constraints = []
        for ac in tree.xpath('/character/additional_constraint'):
            if ac.get('file'):
                text = open(ac.get('file'), 'rb').read()
            else:
                text = ac.text.rstrip(' \r\n\t')
            self.additional_constraints.append(text)

        self.item_ids = []
        for item in tree.xpath('/character/items/item'):
            self.item_ids.append(int(item.text))

class armory_item (armory_base):
    def __init__ (self):
        pass

    def load_item (self, item_id):
        doc = self.load_doc('www.wowhead.com/item=%d&xml' % (item_id),
                            cache = 'cache/%d.xml' % (item_id))

        tree = etree.XML(doc)

        if not tree.xpath('/wowhead/item'):
            return False

        wowhead_json = tree.xpath('/wowhead/item/json')[0].text
        wowhead_jsonEquip = tree.xpath('/wowhead/item/jsonEquip')[0].text

        info = json.loads('{' + wowhead_json + '}')
        equip = json.loads('{' + wowhead_jsonEquip + '}')

        # Translation table from JSON, shamelessly stolen from Rawr.
        socketT = { 2: 'red',
                    4: 'yellow',
                    6: 'orange',
                    8: 'blue',
                   10: 'purple',
                   12: 'green',
                   14: 'prismatic',
                   32: 'cogwheel' }
        socketBonusT = { 3354: { 'stamina': 12 },
                         3305: { 'stamina': 12 },
                         3366: { 'stamina': 12 },
                         4154: { 'stamina': 15 },
                         4134: { 'stamina': 30 },
                         3159: { 'stamina': 45 },
                         4160: { 'hit': 10 },
                         4160: { 'hit': 10 },
                         4151: { 'critical': 10 },
                         4152: { 'critical': 20 },
                         4153: { 'critical': 30 },
                         4142: { 'spirit': 10 },
                         4129: { 'spirit': 20 },
                         4125: { 'spirit': 30 },
                         4143: { 'intellect': 10 },
                         4144: { 'intellect': 20 },
                         4150: { 'intellect': 30 },
                         2782: { 'agility': 10 },
                         4133: { 'agility': 20 },
                         4145: { 'agility': 30 },
                         4184: { 'resilience': 10 },
                         4185: { 'resilience': 20 },
                         4186: { 'resilience': 30 },
                         4135: { 'strength': 10 },
                         4136: { 'strength': 20 },
                         4158: { 'strength': 30 },
                         4146: { 'haste': 10 },
                         4211: { 'haste': 10 },
                         4140: { 'haste': 20 },
                         4128: { 'haste': 30 },
                         4147: { 'parry': 10 },
                         4139: { 'parry': 20 },
                         4123: { 'mastery': 10 },
                         4137: { 'mastery': 20 },
                         4138: { 'mastery': 30 },
                         4155: { 'dodge': 10 },
                         4157: { 'dodge': 30 } }

        self.item_id = info['id']
        self.name = info['name'][1:]
        if 'heroic' in info.keys() and info['heroic'] == 1:
            self.name = '%s (heroic)' % (self.name)
        self.slot = int(info['slot'])
        stats = dict()
        for k in self.equipT.keys():
            if self.equipT[k] in equip.keys():
                stats[k] = equip[self.equipT[k]]
        self.stats = make_stats(stats)
        self.available_sockets = []
        if 'nsockets' in equip.keys():
            for i in range(1,equip['nsockets']+1):
                if equip['socket' + str(i)] in socketT.keys():
                    self.available_sockets.append(socket(socketT[equip['socket' + str(i)]]))
        if self.slot == 6:
            self.available_sockets.append(socket('prismatic'))
        socket_bonus = dict()
        if 'socketbonus' in equip.keys():
            socket_bonus = socketBonusT[equip['socketbonus']]
        self.socket_bonus_stats = make_stats(socket_bonus)

        return True

class item (armory_item):
    def __init__ (self, item_id):
        if self.load_item(item_id):
            self.initialize()
        else:
            raise Exception('Could not load item %d from wowhead.' % item_id)

    def initialize (self):
        self.real_name = '%s %d' % (self.name, random.getrandbits(32))
        self.real_name = self.real_name.replace(':', '_')

        # LP variables
        self.reforge = dict()
        self.enchant = dict()
        self.gems = dict()
        self.socket_bonus = None
        self.total_stats = None

    def get_reforges (self):
        global I

        reforgeable = [ 'spirit', 'haste', 'mastery', 'critical', 'hit',
                        'expertise', 'parry', 'dodge', 'spell penetration',
                        'block' ]
        reforgable = map (lambda x: I[x], reforgeable)
        results = []

        for i in reforgable:
            if self.stats[i] > 0:
                for j in reforgable:
                    if self.stats[j] == 0:
                        num_stats = math.floor(0.40 * self.stats[i])
                        results.append(make_stats({ i: -num_stats,
                                                    j: +num_stats }))

        return results

    __enchant_list = dict({ # Head
                            1: [ enchant(62367), # Arcanum of Hyjal
                                 enchant(62368), # Arcanum of the Dragonmaw
                                 enchant(62366), # Arcanum of the Earthen Ring
                                 enchant(62369), # Arcanum of the Ramkahen
                               ],
                            # Neck
                            2: [ ],
                            # Shoulders
                            3: [ enchant(62343), # Greater Inscription of Charged Lodestone
                                 enchant(62345), # Greater Inscription of Jagged Stone
                                 enchant(62346), # Greater Inscription of Shattered Crystal
                                 enchant(62333), # Greater Inscription of Unbreakable Quartz
                               ],
                            # Chest
                            5: [ enchant(52780), # Greater Stamina
                                 enchant(52758), # Mighty Resilience
                                 enchant(52765), # Exceptional Spirit
                                 enchant(52779), # Peerless Stats
                               ],
                            # Waist
                            6: [ ],
                            # Legs
                            7: [ enchant(56551), # Charscale Leg Armor
                                 enchant(56550), # Dragonscale Leg Armor
                                 enchant(71720), # Drakehide Leg Armor
                                 enchant(54448), # Powerful Enchanted Spellthread
                                 enchant(54450), # Powerful Ghostly Spellthread
                               ],
                            # Feet
                            8: [ enchant(52781), # Assassin's Step
                                 enchant(52743), # Earthen Vitality
                                 enchant(52782)  # Lavawalker
                               ],
                            # Wrist
                            9: [ enchant(68784), # Agility
                                 enchant(68785), # Major Strength
                                 enchant(68786), # Mighty Intellect
                                 enchant(52763), # Dodge
                                 enchant(52770), # Exceptional Spirit
                                 enchant(52778), # Greater Critical Strike
                                 enchant(52772), # Greater Expertise
                                 enchant(52785), # Greater Speed
                                 enchant(52766), # Precision
                                ],
                            # Hands
                            10: [ enchant(52759), # Greater Expertise
                                  enchant(52749), # Haste
                                  enchant(52783), # Mighty Strength
                                  enchant(52784), # Greater Mastery
                                ],
                            # Finger
                            11: [ ],
                            # Trinket
                            12: [ ],
                            # One-handed (weapon)
                            13: [ ],
                            # Ranged (Wand)
                            15: [ ],
                            # Back
                            16: [ enchant(52745), # Greater Spell Penetration
                                  enchant(52777), # Greater Critical Strike
                                  enchant(52773), # Greater Intellect
                                  enchant(52767), # Protection
                                ],
                            # Two-handed (weapon)
                            17: [ ],
                            # Off-hand
                            23: [ enchant(52768) # Superior Intellect
                                ],
                            # Main-hand (weapon)
                            21: [ ],
                            # Relic
                            28: [ ],
                            })

    def get_enchant_list (self):
        return self.__enchant_list[self.slot]

    def get_sockets (self):
        return self.available_sockets

    __gem_list = [ gem(52206), # Bold Inferno Ruby
                   gem(52207), # Brilliant Inferno Ruby
                   gem(52212), # Dedicated Inferno Ruby
                   gem(52216), # Flashing Inferno Ruby
                   gem(52230), # Precise Inferno Ruby
                   gem(52235), # Rigid Ocean Sapphire
                   gem(52242), # Solid Ocean Sapphire
                   gem(52244), # Sparkling Ocean Sapphire
                   gem(52246), # Stormy Ocean Sapphire
                   gem(52218), # Forceful Dream Emerald
                   gem(52223), # Jagged Dream Emerald
                   gem(52225), # Lightning Dream Emerald
                   gem(52227), # Nimble Dream Emerald
                   gem(52228), # Piercing Dream Emerald
                   gem(52231), # Puissant Dream Emerald
                   gem(52233), # Regal Dream Emerald
                   gem(52237), # Sensei's Dream Emerald
                   gem(52245), # Steady Dream Emerald
                   gem(68741), # Vidid Dream Emerald
                   gem(52250), # Zen Dream Emerald
                   gem(52204), # Adept Ember Topaz
                   gem(52205), # Artful Ember Topaz
                   gem(52209), # Deadly Ember Topaz
                   gem(52211), # Deft Ember Topaz
                   gem(52214), # Fiercy Ember Topaz
                   gem(52215), # Fine Ember Topaz
                   gem(52222), # Inscribed Ember Topaz
                   gem(52224), # Keen Ember Topaz
                   gem(68357), # Lucent Ember Topaz
                   gem(52229), # Polished Ember Topaz
                   gem(52239), # Potent Ember Topaz
                   gem(52208), # Reckless Ember Topaz
                   gem(52249), # Resoute Ember Topaz
                   gem(68358), # Replendent Ember Topaz
                   gem(52240), # Skillful Ember Topaz
                   gem(68356), # Willful Ember Topaz
                   gem(52203), # Accurate Demonseye
                   gem(52210), # Defender's Demonseye
                   gem(52213), # Etched Demonseye
                   gem(52220), # Glinting Demonseye
                   gem(52221), # Guardians Demonseye
                   gem(52236), # Purified Demonseye
                   gem(52234), # Retaliating Demonseye
                   gem(52238), # Shifting Demonseye
                   gem(52243), # Sovereight Demonseye
                   gem(52248), # Timeless Demonseye
                   gem(52217), # Veiled Demonseye
                   gem(52219), # Fractured Amberjewel
                   gem(52226), # Mystic Amberjewel
                   gem(52232), # Quick Amberjewel
                   gem(52241), # Smooth Amberjewel
                   gem(52247), # Subtle Amberjewel
                   gem(49110)  # Nightmare Tear
                 ]

    def get_gem_list (self):
        return self.__gem_list

    def get_gems (self):
        return self.gems

    def get_socket_bonus(self):
        return self.socket_bonus_stats

    def get_name (self):
        return self.name

    def solve (self, problem, used):
        #
        # forall (reforge_stats in get_reforges()):
        #     variable: reforge[item_id,i] in [0,1]
        #     set: reforge_stats[item_id,i] in [-Inf,Inf]^4
        # variable: reforge_stats[item_id] in [-Inf,Inf]^4
        # post: sum (reforge[item_id,:]) <= 1 * used
        # post: sum (reforge[item_id,:] * reforge_stats[item_id,:]) = reforge_stats[item_id]
        reforge_num = 0
        for x in self.get_reforges():
            var = pulp.LpVariable(self.real_name + " reforge[" + str(reforge_num) + "]", 0, 1, 'Integer')
            self.reforge[var] = x
            reforge_num = reforge_num + 1
        if self.reforge.keys():
            problem += pulp.lpSum(self.reforge.keys()) <= 1 * used

        reforge_stats = make_stats({}, default = lambda i: pulp.LpVariable(self.real_name + " reforge_stats[" + str(i) + "]", cat = 'Integer'))
        for i in range(len(reforge_stats)):
            problem += pulp.lpSum(r * self.reforge[r][i] for r in self.reforge.keys()) == reforge_stats[i]

        #
        # forall (i in get_enchant_list()):
        #     variable: enchant[item_id,i] in [0,1]
        #     set: enchant_stats[item_id,i] in [0,Inf]^4
        # variable: enchant_stats[item_id]
        # post: sum (enchant[item_id,:]) = 1 * used
        # post: sum (enchant_stats[item_id,:] * enchant[item_id,:]) = enchant_stats[item_id]
        enchant_num = 0
        for x in self.get_enchant_list():
            var = pulp.LpVariable(self.real_name + " enchant[" + str(enchant_num) + "]", 0, 1, 'Integer')
            self.enchant[var] = x
            enchant_num = enchant_num + 1
        if self.enchant.keys():
            problem += pulp.lpSum(self.enchant.keys()) == 1 * used

        enchant_stats = make_stats({}, default = lambda i: pulp.LpVariable(self.real_name + " enchant_stats[" + str(i) + "]", 0, cat = 'Integer'))
        for i in range(len(enchant_stats)):
            problem += pulp.lpSum(e * self.enchant[e].stats[i] for e in self.enchant.keys()) == enchant_stats[i]

        #
        # forall (i in get_sockets()):
        #     forall (j in get_gem_list()):
        #         variable: gem[item_id,i,j] in [0,1]
        #         set: gem_colour[item_id,i,j] in [0,1]
        #         set: gem_stats[item_id,i,j] in [0,Inf]^4
        #     post: sum (gem[item_id,i,:]) = 1 * used
        # variable: gem_colour[item_id] in [0,1]
        # variable: gem_stats[item_id]
        # set: socket_bonus[item_id] in [0,Inf]^4
        # set: num_sockets in [0,Inf]
        # post: sum (gem_colour[item_id,:,:] * gem[item_id,:,:]) / num_socket = gem_colour[item_id]
        # post: sum (gem_stats[item_id,:,:] * gem[item_id,:,:]) + ...
        #       gem_colour[item_id] * socket_bonus[item_id] = gem_stats[item_id]
        gem_colour = dict()
        socket_num = 1

        for socket in self.get_sockets():
            gem_ = []

            for i in self.get_gem_list():
                var = pulp.LpVariable(self.real_name + " gem[" + str(socket_num) + "," + str(i.id) + "]", 0, 1, cat = 'Integer')
                gem_colour[var] = socket.matches(i)
                self.gems[var] = i
                gem_.append(var)

            problem += pulp.lpSum(gem_) == 1 * used
            socket_num = socket_num + 1

        num_sockets = len(self.get_sockets())
        self.socket_bonus = pulp.LpVariable(self.real_name + " socket_bonus", 0, 1, 'Integer')
        socket_bonus_stats = self.get_socket_bonus()
        problem += pulp.lpSum(1.0 / num_sockets * gem_colour[g] * g for g in self.gems.keys()) >= self.socket_bonus

        gem_stats = make_stats({})

        for i in range(len(gem_stats)):
            gem_stats[i] = pulp.LpVariable(self.real_name + " gem_stats[" + str(i) + "]", 0, cat = 'Integer')
            problem += pulp.lpSum(self.gems[g].stats[i] * g for g in self.gems.keys()) + self.socket_bonus * socket_bonus_stats[i] == gem_stats[i]

        #
        # variable total_stats[item_id] in [0,Inf]^4
        # set: starting_stats = [0,Inf]^4
        # post: used * starting_stats + gem_stats[item_id] + ...
        #                               reforge_stats[item_id] + ...
        #                               enchant_stats[item_id] = total_stats[item_id]
        # return total_stats[item_id]
        self.total_stats = make_stats({}, default = lambda i: pulp.LpVariable(self.real_name + '[' + str(i) + ']', 0, cat = 'Integer'))
        for i in range(len(self.total_stats)):
            problem += used * self.stats[i] + reforge_stats[i] + enchant_stats[i] + gem_stats[i] == self.total_stats[i]
        return self.total_stats

    def print_results (self):
        print '<item>'
        print '<id><![CDATA[%d]]></id>' % (self.item_id)
        print '<name><![CDATA[%s]]></name>' % (self.name)
        print '<base>%s</base>' % fmt_stats(self.stats)

        for g in self.gems.keys():
            if pulp.value(g) == 1:
                print '<gem name="%s">%s</gem>' % (self.gems[g].name, fmt_stats(self.gems[g].stats))

        if pulp.value(self.socket_bonus) == 1:
            print '<socket_bonus>%s</socket_bonus>' % fmt_stats(self.get_socket_bonus())
        elif self.get_sockets():
            print '<socket_bonus></socket_bonus>'

        for e in self.enchant.keys():
            if pulp.value(e) == 1:
                print '<enchant name="%s">%s</enchant>' % (self.enchant[e].name, fmt_stats(self.enchant[e].stats))

        for r in self.reforge.keys():
            if pulp.value(r) == 1:
                print '<reforge>%s</reforge>' % fmt_stats(self.reforge[r])
        print '</item>'

class character (armory_character, xml_character):
    def __init__ (self, fd):
        xml_character.load_character(self, fd)

        if not self.is_loaded:
            armory_character.load_character(self, self.name, self.realm, self.region)

        self.items = dict()
        self.used = dict()

        # LP variable
        self.total_stats = make_stats({})

        for item_id in self.item_ids:
            self.add_item(item(item_id))

    def add_item (self, item):
        if not item.slot in self.items:
            self.items[item.slot] = []
        self.items[item.slot].append(item)

    def get_items (self):
        results = []

        for slot in self.items.keys():
            for item in self.items[slot]:
                results.append(item)
        return results

    def get_gems (self):
        results = dict()

        for item in self.used.keys():
            for g in item.gems:
                results[g] = item.gems[g]
        return results

    def get_reforges (self):
        results = dict()

        for slot in self.items.keys():
            for item in self.items[slot]:
                for var in item.reforge.keys():
                    results[var] = item.reforge[var]
        return results

    def solve (self):
        #
        # forall (i in get_items()):
        #     item[i] = i.print_mip()
        # forall (slot in get_slots()):
        #     post: sum (item[slot,:]) = 1
        # forall (i in get_items()):
        #     post: sum (item[:,:] if item[:,:].name == i.name) <= 1
        problem = pulp.LpProblem("World of Warcraft Optimizer", pulp.LpMaximize)
        item_stats = dict()

        for slot in self.items.keys():
            for item in self.items[slot]:
                self.used[item] = pulp.LpVariable("used[" + item.real_name + "]", 0, 1, 'Integer')
                item_stats[item] = item.solve(problem, self.used[item])
            if self.items[slot]:
                if slot in [ 11, 12, 13 ]: # Trinket, Ring, One-handed
                    num_in_slot = 2
                else:
                    num_in_slot = 1
                problem += pulp.lpSum(self.used[item] for item in self.items[slot]) <= num_in_slot

        for item in self.used.keys():
            duplicates = [ self.used[i] for i in self.used.keys() if i.get_name() == item.get_name() ]

            if len(duplicates) > 1:
                problem += pulp.lpSum(duplicates) <= 1

        #
        # variable: slot_17 in [0,1]
        # post: slot_17 == sum (used[item] for item in items[17,:])
        # for slot in [ 13, 14, 21, 23 ]:
        #     variable: slot_used in [0,1]
        #     post: slot_used = sum (used[item] for item in items[slot,:])
        #     post: slot_used <= 1 - slot_17
        if 17 in self.items.keys():
            slot_used_17 = pulp.LpVariable('slot_used[17]', 0, 1, 'Integer')

            if 17 in self.items.keys():
                problem += slot_used_17 == pulp.lpSum(self.used[item] for item in self.items[17])
            else:
                problem += slot_used_17 == 0

            for slot in set([ 13, 14, 21, 23 ]) & set(self.items.keys()):
                slot_used = pulp.LpVariable('slot_used[' + str(slot) + ']', 0, 1, 'Integer')
                problem += slot_used == pulp.lpSum(self.used[item] for item in self.items[slot])
                problem += slot_used <= 1 - slot_used_17

        #
        # variable: total_stats in [0,Inf]^4
        # post: sum (item[i]) = total_stats
        for i in range(len(self.total_stats)):
            self.total_stats[i] = pulp.LpVariable("total_stats[" + str(i) + "]", 0, cat = 'Integer')
            problem += pulp.lpSum(s[i] for s in item_stats.values()) + self.base_stats[i] == self.total_stats[i]

        #
        # var: penalty in [0,Inf]
        # post: additional contraints
        # objective function: weight[:] * total_stats[:]
        #
        # solve it
        self.penalty = pulp.LpVariable('penalty', 0, cat = 'Integer')

        for ac in self.additional_constraints:
            def N (name):
                return '%s[%s]' % (name, '')
            global I, G

            exec ac in globals(), locals()

        # problem.writeLP('debug.lp')
        problem.sequentialSolve([
                pulp.lpDot(self.weight, self.total_stats) - self.penalty,
                pulp.lpSum(self.total_stats) ])

        return problem.status

    def print_results (self):
        print '<total>%s</total>' % fmt_stats(map (lambda x: pulp.value(x), self.total_stats))
        print '<base>%s</base>' % fmt_stats(self.base_stats)

        print '<items>'
        for item_list in self.items.values():
            for item in item_list:
                if pulp.value(self.used[item]) == 1:
                    item.print_results()
        print '</items>'

try:
    ## Parse the command-line arguments.
    parser = optparse.OptionParser(usage = '%prog [options] [character]')
    parser.add_option('--item', action = 'append', type = 'int', dest = 'items')
    parser.add_option('--stdin', action = 'store_true')

    (options, args) = parser.parse_args()

    if args:
        fd = open(args[0], 'rb')

        try:
            char = character(fd)
        finally:
            fd.close()
    elif options.stdin:
        char = character(sys.stdin)
    else:
        parser.print_help()
        sys.exit(1)

    for item_id in options.items or []:
        char.add_item(item(item_id))

    ## Solve it and print the results.
    result = char.solve()

    print '<character>'
    print '<status><![CDATA[%s]]></status>' % (pulp.LpStatus[result])

    if pulp.LpStatus[result] == 'Optimal':
        char.print_results()
    else:
        print '<message><![CDATA[%s]]></message>' % pulp.LpStatus[result]

    print '</character>'
except Exception as e:
    print '<character><status>Error</status><message><![CDATA[%s]]></message></character>' % (e)
    sys.exit(1)
