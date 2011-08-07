bonus_5percent_int = pulp.LpVariable(N('bonus_5percent_int'), 0, cat = 'Integer')

problem += bonus_5percent_int <= 1.05 * self.total_stats[I['intellect']]
self.total_stats[I['intellect']] = bonus_5percent_int
