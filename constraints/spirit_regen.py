# Spirit Regen = 0.016725 * sqrt(int) * spi
#
import math

def solve_min (problem, x):
    problem += -x
    problem.solve()

    if pulp.LpStatus[problem.status] == 'Optimal':
        return int(pulp.value(x))
    else:
        return 0

def solve_max (problem, x):
    problem += x
    problem.solve()

    if pulp.LpStatus[problem.status] == 'Optimal':
        return int(pulp.value(x))
    else:
        return 0

num_segment = 10
int_min = solve_min(problem, self.total_stats[I['intellect']])
int_max = solve_max(problem, self.total_stats[I['intellect']])
int_x = range(int_min, int_max, max(1, (int_max - int_min) / num_segment)) + [ int_max]
spi_min = solve_min(problem, self.total_stats[I['spirit']])
spi_max = solve_max(problem, self.total_stats[I['spirit']])
spi_x = range(spi_min, spi_max, max(1, (spi_max - spi_min) / num_segment)) + [ spi_max]

self.spirit_regen = pulp.LpVariable(N('spirit_regen'))
points = {}

for i in range(len(int_x)):
    for j in range(len(spi_x)):
        points[(i,j)] = 0.016725 * math.sqrt(int_x[i]) * spi_x[j]

points_var = []
points_int = []
points_spi = []
points_mp5 = []
points_s = {}

for (i,j) in points.keys():
    try:
        base_name = 'points_x[' + str(i) + ',' + str(j) + ']'

        int0 = int_x[i+0]
        int1 = int_x[i+1]
        spi0 = spi_x[j+0]
        spi1 = spi_x[j+1]

        x00 = pulp.LpVariable(base_name + '[0,0]', 0, 1)
        x01 = pulp.LpVariable(base_name + '[0,1]', 0, 1)
        x10 = pulp.LpVariable(base_name + '[1,0]', 0, 1)
        x11 = pulp.LpVariable(base_name + '[1,1]', 0, 1)

        points_int += [ x00 * int0, x01 * int0, x10 * int1, x11 * int1 ]
        points_spi += [ x00 * spi0, x01 * spi1, x10 * spi0, x11 * spi1 ]
        points_mp5 += [ x00 * points[(i,j)], x01 * points[(i,j+1)],
                        x10 * points[(i+1,j)], x11 * points[(i+1,j+1)] ]
        points_var += [ x00, x01, x10, x11 ]

        points_s[(i,j)] = pulp.LpVariable('points_s[' + str(i) + ',' + str(j) + ']', 0, 1, cat = 'Integer')
        problem += x00 + x01 + x10 + x11 == points_s[(i,j)]
    except IndexError:
        pass
    except KeyError:
        pass

problem += pulp.lpSum(points_var) == 1
problem += pulp.lpSum(points_s.values()) == 1 # Redundant
problem += pulp.lpSum(points_int) == self.total_stats[I['intellect']]
problem += pulp.lpSum(points_spi) == self.total_stats[I['spirit']]
problem += pulp.lpSum(points_mp5) == self.spirit_regen

# Woot, self.spirit_regen is now an approximation of 0.016725 * sqrt(int) * spi!
