gems = self.get_gems()
red_socket = socket('red')
red_gems = [ g for g in gems.keys() if red_socket.matches(gems[g]) ]

problem += pulp.lpSum(red_gems) >= 3
