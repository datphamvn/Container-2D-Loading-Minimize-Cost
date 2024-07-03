from ortools.linear_solver import pywraplp


def input_data():
    data = {}
    n, k = map(int, input().split())
    data['size_item'] = []
    data['size_truck'] = []
    data['cost'] = []

    for i in range(n):
        w, h = map(int, input().split())
        data['size_item'].append([w, h])

    for _ in range(k):
        w, h, c = map(int, input().split())
        data['size_truck'].append([w, h])
        data['cost'].append(c)

    W_truck = [data['size_truck'][i][0] for i in range(k)]
    H_truck = [data['size_truck'][i][1] for i in range(k)]
    return n, k, data, W_truck, H_truck


n, k, data, W_truck, H_truck = input_data()
# W_truck is the list of width of trucks
# H_truck is the list of length of trucks
# n is the number of item
# k is the number of truck

max_W = max(W_truck)
max_H = max(H_truck)

# Create Solver
solver = pywraplp.Solver.CreateSolver('SCIP')

# Create variables
M = 1000000

z = {}  # z[(i,m)] = 1 if item i is packed in truck m else 0
o = {}  # if o = 1 then rotation = 90 degree, else 0
l = {}  # left coordination of item
b = {}  # bottom coodination of item
r = {}  # right coordination of item
t = {}  # top coordination of item

for i in range(n):
    o[i] = solver.IntVar(0, 1, 'o[%i] ' % i)
    # # coordinate of item i
    l[i] = solver.IntVar(0, max_W, 'l[%i]' % i)
    r[i] = solver.IntVar(0, max_W, 'r[%i]' % i)
    t[i] = solver.IntVar(0, max_H, 't[%i]' % i)
    b[i] = solver.IntVar(0, max_H, 'b[%i]' % i)

    solver.Add(r[i] == l[i] + (1 - o[i]) * data['size_item'][i][0] + o[i] * data['size_item'][i][1])
    solver.Add(t[i] == b[i] + (1 - o[i]) * data['size_item'][i][1] + o[i] * data['size_item'][i][0])

    for m in range(k):
        z[(i, m)] = solver.IntVar(0, 1, 'z_[%i]_[%i]' % (i, m))

        # item i must not exceed area of truck
        solver.Add(r[i] <= (1 - z[(i, m)]) * M + W_truck[m])
        solver.Add(l[i] <= (1 - z[(i, m)]) * M + W_truck[m])
        solver.Add(t[i] <= (1 - z[(i, m)]) * M + H_truck[m])
        solver.Add(b[i] <= (1 - z[(i, m)]) * M + H_truck[m])

    # each item must be pack in 1 truck
for i in range(n):
    solver.Add(sum(z[(i, m)] for m in range(k)) == 1)

# if 2 items is packed in the same truck, they must be not overlaped
for i in range(n - 1):
    for j in range(i + 1, n):
        for m in range(k):
            # add varirable e = z[i,m] x z[j,m]
            e = solver.IntVar(0, 1, f'e[{i}][{j}]')
            solver.Add(e >= z[i, m] + z[j, m] - 1)
            solver.Add(e <= z[i, m])
            solver.Add(e <= z[j, m])

            # Binary variables for each constraint
            c1 = solver.IntVar(0, 1, f'c1[{i}][{j}]')
            c2 = solver.IntVar(0, 1, f'c2[{i}][{j}]')
            c3 = solver.IntVar(0, 1, f'c3[{i}][{j}]')
            c4 = solver.IntVar(0, 1, f'c4[{i}][{j}]')

            # Constraints that the binary variables must satisfy
            solver.Add(r[i] <= l[j] + M * (1 - c1))
            solver.Add(r[j] <= l[i] + M * (1 - c2))
            solver.Add(t[i] <= b[j] + M * (1 - c3))
            solver.Add(t[j] <= b[i] + M * (1 - c4))

            solver.Add(c1 + c2 + c3 + c4 + (1 - e) * M >= 1)
            solver.Add(c1 + c2 + c3 + c4 <= e * M)
# find trucks be used
used = {}  # used [m] = 1 if truck m be used
for m in range(k):
    used[m] = solver.IntVar(0, 1, 'used[%i] ' % m)
    # if sum(z[i][m]) >= 1 then truck m be used => used[m] = 1
    # else, used[m] = 0

    q = solver.IntVar(0, n, f'q[{m}]')
    solver.Add(q == sum(z[(i, m)] for i in range(n)))
    # truck m be used if there are at least 1 item be packed in it, so sum(z[(i,m)] for i in range(n)) != 0

    # q = 0 => used[m] = 0
    # q != 0 => used[m] = 1
    solver.Add(used[m] <= q * M)
    solver.Add(q <= used[m] * M)

# objective
cost = sum(used[m] * data['cost'][m] for m in range(k))
solver.Minimize(cost)
time_limit = 0.5 * 200000
solver.set_time_limit(int(time_limit))

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    for i in range(n):
        print(f'{i + 1}', end=' ')
        for j in range(k):
            if z[i, j].solution_value() == 1:
                print(f'{j + 1}', end=' ')
        print(f'{int(l[i].solution_value())} {int(b[i].solution_value())}', end=' ')
        print(f'{int(o[i].solution_value())}')
    print(f'Number of bin used  :', int(sum(used[m].solution_value() for m in range(k))))
    print(f'Total cost          : {solver.Objective().Value()}')
    print(f'Time limit          : {time_limit}')
    print(f'Running time        : {solver.WallTime() / 1000}')