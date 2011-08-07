bonus_4percent_parry = pulp.LpVariable(N('bonus_4percent_parry'), 0, cat = 'Integer')

problem += bonus_4percent_parry <= 1.04 * self.total_stats[I['parry']]

self.total_stats[I['parry']] = bonus_4percent_parry
