import os
import time
from ortools.linear_solver import pywraplp


def input_data(testcase_path):
    data = {}
    with open(testcase_path, 'r') as f:
        lines = f.readlines()

    n, k = map(int, lines[0].split())
    data['size_item'] = []
    data['size_truck'] = []
    data['cost'] = []

    for i in range(n):
        w, h = map(int, lines[1 + i].split())
        data['size_item'].append([w, h])

    for j in range(k):
        w, h, c = map(int, lines[1 + n + j].split())
        data['size_truck'].append([w, h])
        data['cost'].append(c)

    W_truck = [data['size_truck'][i][0] for i in range(k)]
    H_truck = [data['size_truck'][i][1] for i in range(k)]
    return n, k, data, W_truck, H_truck


def process_test_case(testcase_path):
    n, k, data, W_truck, H_truck = input_data(testcase_path)

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

    # each item must be packed in 1 truck
    for i in range(n):
        solver.Add(sum(z[(i, m)] for m in range(k)) == 1)

    # if 2 items are packed in the same truck, they must not overlap
    for i in range(n - 1):
        for j in range(i + 1, n):
            for m in range(k):
                # add variable e = z[i,m] x z[j,m]
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

    # find trucks being used
    used = {}  # used [m] = 1 if truck m is used
    for m in range(k):
        used[m] = solver.IntVar(0, 1, 'used[%i] ' % m)
        # if sum(z[i][m]) >= 1 then truck m is used => used[m] = 1
        # else, used[m] = 0

        q = solver.IntVar(0, n, f'q[{m}]')
        solver.Add(q == sum(z[(i, m)] for i in range(n)))
        # truck m is used if there are at least 1 item packed in it, so sum(z[(i, m)] for i in range(n)) != 0

        # q = 0 => used[m] = 0
        # q != 0 => used[m] = 1
        solver.Add(used[m] <= q * M)
        solver.Add(q <= used[m] * M)

    # objective
    cost = sum(used[m] * data['cost'][m] for m in range(k))
    solver.Minimize(cost)
    time_limit = 0.5 * 200000
    solver.set_time_limit(int(time_limit))

    start_time = time.time()
    status = solver.Solve()
    end_time = time.time()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        result = []
        for i in range(n):
            item_result = [i + 1]
            for j in range(k):
                if z[i, j].solution_value() == 1:
                    item_result.append(j + 1)
            item_result.append(int(l[i].solution_value()))
            item_result.append(int(b[i].solution_value()))
            item_result.append(int(o[i].solution_value()))
            result.append(item_result)

        num_trucks_used = int(sum(used[m].solution_value() for m in range(k)))
        total_cost = solver.Objective().Value()
        running_time = end_time - start_time

        return result, num_trucks_used, total_cost, running_time
    else:
        return None, None, None, None


# Directory containing test cases
testcase_folder = 'testcase'

# Process each test case in the folder
for testcase_filename in os.listdir(testcase_folder):
    testcase_path = os.path.join(testcase_folder, testcase_filename)
    result, num_trucks_used, total_cost, running_time = process_test_case(testcase_path)

    if result is not None:
        print(f"Test case {testcase_filename}:")
        for item_result in result:
            print(' '.join(map(str, item_result)))
        print(f'Number of trucks used: {num_trucks_used}')
        print(f'Total cost: {total_cost}')
        print(f'Running time: {running_time:.4f} seconds')
    else:
        print(f"Test case {testcase_filename}: No feasible solution found")
