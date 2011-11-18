trinkets = { # Fall of Mortality (15% uptime)
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

for item in self.get_items():
    item_id = item.item_id

    if item_id in trinkets.keys():
        trinket_bonus = make_stats(trinkets[item_id])

        for i in range(len(self.total_stats)):
            if not trinket_bonus[i] == 0:
                trinket_stats = pulp.LpVariable('trinket_bonus[' + str(item_id) + ',' + str(i) + ']', 0)
                problem += trinket_stats == trinket_bonus[i] * self.used[item] + self.total_stats[i]
                self.total_stats[i] = trinket_stats
