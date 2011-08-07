gems = self.get_gems()
yellow_socket = socket('Yellow')
yellow_gems = [ g for g in gems.keys() if yellow_socket.matches(gems[g]) ]

problem += pulp.lpSum(yellow_gems) >= 2
