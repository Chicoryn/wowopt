prof_60_int = pulp.LpVariable(N('prof_60_int'), 0)

problem += prof_60_int == self.total_stats[I['intellect']] + 60
self.total_stats[I['intellect']] = prof_60_int
