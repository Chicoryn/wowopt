t12_items = [ 71272, 71528, 71531, 71275, 71530, 71274, 71529, 71273, 71532, 71278 ]
t12_items = [ item for item in self.get_items() if item.item_id in t12_items ]

if len(t12_items) >= 2:
    t12_2p_used = pulp.LpVariable(N('t12_2p_used'), 0, 1, 'Integer')
    t12_2p_spirit = pulp.LpVariable(N('t12_2p_spirit'), 0, cat = 'Integer')
    t12_4p_used = pulp.LpVariable(N('t12_4p_used'), 0, 1, 'Integer')
    t12_4p_hps = pulp.LpVariable(N('t12_4p_hps'), 0, cat = 'Integer')

    problem += pulp.lpSum([ 0.25 * self.used[item] for item in t12_items ]) >= t12_4p_used
    problem += pulp.lpSum([ 0.5 * self.used[item] for item in t12_items ]) >= t12_2p_used

    problem += t12_2p_spirit == self.total_stats[I['spirit']] + 411 * t12_2p_used
    problem += t12_4p_hps == self.total_stats[I['hps']] + 400 * t12_4p_used

    self.total_stats[I['spirit']] = t12_2p_spirit
    self.total_stats[I['hps']] = t12_4p_hps
