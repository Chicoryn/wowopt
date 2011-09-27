# Spirit Regen = 0.16 * sqrt(int) * spi
#
# Basic idea is to approximate sqrt(int) using a piecewise-linear function,
# and then to approximate sqrt(int) * spi using bilinear filtering.
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

int_min = solve_min(problem, self.total_stats[I['intellect']])
int_max = solve_max(problem, self.total_stats[I['intellect']])
int_x = range(int_min, int_max, max(1, (int_max - int_min) / 10))
spi_min = solve_min(problem, self.total_stats[I['spirit']])
spi_max = solve_max(problem, self.total_stats[I['spirit']])

int_z = map(lambda x: pulp.LpVariable('spirit_regen_int_z[%s]' % x, cat = 'Binary'), int_x)
int_s = map(lambda x: pulp.LpVariable('spirit_regen_int_s[%s]' % x, 0, 1), int_x)
int_y = map(lambda x: math.sqrt(x), int_x)

problem += pulp.lpSum(int_z) == 1

for i in range(len(int_x)):
    problem += int_s[i] <= int_z[i]

int_xe = pulp.LpAffineExpression()
int_ye = pulp.LpAffineExpression()
for i in range(len(int_x)-1):
    int_xe = int_xe + int_x[i] * int_z[i] + \
                      (int_x[i+1] - int_x[i]) * int_s[i]
    int_ye = int_ye + int_y[i] * int_z[i] + \
                      (int_y[i+1] - int_y[i]) * int_s[i]

sqrt_int = pulp.LpVariable('spirit_regen_sqrt_int')

problem += int_xe == self.total_stats[I['intellect']]
problem += int_ye == sqrt_int

# Note: sqrt_int is now an approximation of sqrt(int)

spi = self.total_stats[I['spirit']]
spi_int = pulp.LpVariable('spirit_regen_int_spi', spi_min * min(int_y), spi_max * max(int_y))

# x1 = sqrt_int
# x2 = spi
problem += spi_min * sqrt_int + min(int_y) * spi - spi_min * min(int_y) <= spi_int
problem += spi_int <= spi_min * sqrt_int + max(int_y) * spi - max(int_y) * spi_min

problem += spi_max * sqrt_int + max(int_y) * spi - spi_max * max(int_y) <= spi_int
problem += spi_int <= spi_max * sqrt_int + min(int_y) * spi - min(int_y) * spi_max

# Note: spi_int is now an approximation of sqrt(int) * spi

self.spirit_regen = pulp.LpVariable('spirit_regen', 0)

problem += self.spirit_regen == 0.016725 * spi_int

# Woot, self.spirit_regen is now an approximation of 0.016725 * sqrt(int) * spi!
