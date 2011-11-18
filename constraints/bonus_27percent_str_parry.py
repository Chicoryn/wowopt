bonus_27percent_str_parry = pulp.LpVariable(N('bonus_27percent_str_parry'), 0)

problem += bonus_27percent_str_parry == self.total_stats[I['parry']] + 0.27 * self.total_stats[I['strength']]

self.total_stats[I['parry']] = bonus_27percent_str_parry
