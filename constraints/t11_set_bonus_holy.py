t11_items = [ 65230, 65233, 65232, 65229, 65231 ]
t11_4p = [ item for item in self.get_items() if item.item_id in t11_items ]

if len(t11_4p) >= 4:
    t11_4p_used = pulp.LpVariable(N('t11_4p_used'), 0, 1, 'Integer')
    t11_4p_spirit = pulp.LpVariable(N('t11_4p_spirit'), 0)

    problem += pulp.lpSum([ 0.25 * self.used[item] for item in t11_4p ]) >= t11_4p_used

    problem += t11_4p_spirit == self.total_stats[I['spirit']] + 540 * t11_4p_used
    self.total_stats[I['spirit']] = t11_4p_spirit
