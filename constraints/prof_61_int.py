prof_61_int = pulp.LpVariable(N('prof_61_int'), 0, cat = 'Integer')

problem += prof_61_int == self.total_stats[I['intellect']] + 61
self.total_stats[I['intellect']] = prof_61_int
