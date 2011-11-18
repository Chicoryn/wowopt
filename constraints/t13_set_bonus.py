t13_items = [ 78842, 76361, 78747, 78700, 76358, 78795, 78728, 76360, 78823, 78719, 76359, 78814, 78683, 76357, 78778 ]
t13_items = [ item for item in self.get_items() if item.item_id in t13_items ]

if len(t13_items) >= 2:
    t13_2p_used = pulp.LpVariable(N('t13_2p_used'), 0, 1, 'Integer')
    t13_2p_mp5 = pulp.LpVariable(N('t13_2p_mp5'), 0)
    t13_4p_used = pulp.LpVariable(N('t13_4p_used'), 0, 1, 'Integer')
    t13_4p_hps = pulp.LpVariable(N('t13_4p_hps'), 0)

    problem += pulp.lpSum([ 0.25 * self.used[item] for item in t13_items ]) >= t13_4p_used
    problem += pulp.lpSum([ 0.5 * self.used[item] for item in t13_items ]) >= t13_2p_used

    problem += t13_2p_mp5 == self.total_stats[I['mp5']] + 111 * t13_2p_used
    problem += t13_4p_hps == self.total_stats[I['hps']] + 250 * t13_4p_used

    self.total_stats[I['mp5']] = t13_2p_mp5
    self.total_stats[I['hps']] = t13_4p_hps
