meta_54_int = pulp.LpVariable(N('meta_54_int'), 0, cat = 'Integer')

problem += meta_54_int == 54 + self.total_stats[I['intellect']]
self.total_stats[I['intellect']] = meta_54_int
