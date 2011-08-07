bonus_15percent_int = pulp.LpVariable(N('bonus_15percent_int'), 0, cat = 'Integer')

problem += bonus_15percent_int <= 1.15 * self.total_stats[I['intellect']]
self.total_stats[I['intellect']] = bonus_15percent_int
