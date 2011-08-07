bonus_100percent_spirit_hit = pulp.LpVariable(N('bonus_100percent_spirit_hit'), 0, cat = 'Integer')

problem += bonus_100percent_spirit_hit <= self.total_stats[I['spirit']] + self.total_stats[I['hit']]

self.total_stats[I['hit']] = bonus_100percent_spirit_hit
