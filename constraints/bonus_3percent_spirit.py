bonus_3percent_spirit = pulp.LpVariable(N('bonus_3percent_spirit'), 0)

problem += bonus_3percent_spirit == 1.03 * self.total_stats[I['spirit']]
self.total_stats[I['spirit']] = bonus_3percent_spirit
