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
             69149: { 'hps': 355 }
           }

for item in self.get_items():
    item_id = item.item_id

    if item_id in trinkets.keys():
        trinket_bonus = make_stats(trinkets[item_id])

        for i in range(len(self.total_stats)):
            if not trinket_bonus[i] == 0:
                trinket_stats = pulp.LpVariable('trinket_bonus[' + str(item_id) + ',' + str(i) + ']', 0, cat = 'Integer')
                problem += trinket_stats == trinket_bonus[i] * self.used[item] + self.total_stats[i]
                self.total_stats[i] = trinket_stats
