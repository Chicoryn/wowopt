procs = { ## Enchants ##
          # Power Torrent (25% uptime) (jsonUse say 500, so we need to negate that)
          52774: { 'intellect': -375 },
          # Heartsong (54% uptime) (jsonUse say 200, so we need to negate that)
          52761: { 'spirit': -92 },
          # Landslide (25% uptime)
          52776: { 'attack power': 250 },
          # Hurricane (20% uptime) (jsonUse say 450, so we need to negate that)
          52760: { 'haste': -360 },
          # Windwalk (30% uptime)
          52775: { 'dodge': 180 },

          ## Trinkets ##
          # Fall of Mortality (15% uptime)
          59500: { 'spirit': 289 },
          # Fall of Mortaility (heroic) (15% uptime)
          65124: { 'spirit': 326 },
          # Shard of Woe (1.5s gcd)
          60233: { 'mp5': 1350, 'haste': 322 },
          # Jaws of Defeat (1.5s gcd)
          68926: { 'mp5': 390 },
          # Jaws of Defeat (heroic) (1.5s gcd)
          69111: { 'mp5': 440 },
          # Eye of Blazing Power
          68983: { 'hps': 355 },
          # Eye of Blazing Power (heroic)
          69149: { 'hps': 355 },
          # Reflection of the Light
          77115: { 'spell power': 382 },
          # Bottled Wishes
          77114: { 'spell power': 382 },
          # Will of the Unbinding (heroic)
          77995: { 'intellect': 990 },
          # Will of the Unbinding
          77198: { 'intellect': 880 },
          # Will of the Unbinding (LFR)
          77975: { 'intellect': 780 },
          # Heart of Unliving (heroic)
          77996: { 'spirit': 990 },
          # Heart of Unliving
          77199: { 'spirit': 880 },
          # Heart of Unliving (LFR)
          77976: { 'spirit': 780 },
          # Seal of the Seven Signs (heroic) (20% uptime)
          77989: { 'haste': 655 },
          # Seal of the Seven Signs (20% uptime)
          77204: { 'haste': 580 },
          # Seal of the Seven Signs (LFR) (20% uptime)
          77969: { 'haste': 514 },
          # Windward Heart (heroic) (45s icd)
          78001: { 'hps': 281 },
          # Windward Heart (45s icd)
          77209: { 'hps': 249 },
          # Windward Heart (LFR) (45s icd)
          77981: { 'hps': 221 },
          
          ## Weapons ##
          # Maw of the Dragonlord (heroic) (15s icd, 6 targets average)
          78476: { 'hps': 2980 },
          # Maw of the Dragonlord (15s icd, 6 targets average)
          77196: { 'hps': 2640 },
          # Maw of the Dragonlord (LFR) (15s icd, 6 targets average)
          78485: { 'hps': 2338 },
          # Ti'tahk, the Steps of Time (heroic) (45s icd)
          78477: { 'haste': 483 },
          # Ti'tahk, the Steps of Time (45s icd)
          77190: { 'haste': 428 },
          # Ti'tahk, the Steps of Time (LFR) (45s icd)
          78486: { 'haste': 379 },
         }

def add_bonus_proc (id, problem, total_stats, used, bonus):
    bonus_stats = make_stats(bonus)

    for i in range(len(bonus_stats)):
        if not bonus_stats[i] == 0:
            bonus_var = pulp.LpVariable('bonus_proc[' + id + ',' + str(i) + ']')

            problem += bonus_var == bonus_stats[i] * used + total_stats[i]
            total_stats[i] = bonus_var

for item in self.get_items():
    item_id = item.item_id

    for used, enchant in item.enchant.items():
        if enchant.id in procs:
            add_bonus_proc(str(item_id) + ',' + str(enchant.id),
			               problem, self.total_stats, used, procs[enchant.id])

    if item_id in procs:
        add_bonus_proc(str(item_id), problem, self.total_stats, self.used[item], procs[item_id])
