import os
import time
from ortools.sat.python import cp_model


def input_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = {}
    data['N'], data['K'] = map(int, lines[0].split())  # Number of items and trucks

    data['items'] = []
    for i in range(1, data['N'] + 1):
        w, h = map(int, lines[i].split())
        data['items'].append((w, h))

    data['trucks'] = []
    for i in range(data['N'] + 1, data['N'] + data['K'] + 1):
        w, h, c = map(int, lines[i].split())
        data['trucks'].append((w, h, c))

    return data


def process_test_case(data, time_limit):
    N = data['N']
    K = data['K']
    items = data['items']
    trucks = data['trucks']

    max_width = max(x[0] for x in trucks)
    max_height = max(x[1] for x in trucks)

    model = cp_model.CpModel()

    X = {}
    R = []
    for i in range(N):
        R.append(model.NewBoolVar(f'item_{i}_rotated'))
        for j in range(K):
            X[i, j] = model.NewBoolVar(f'item_{i}_in_truck_{j}')

    Z = [model.NewBoolVar(f'truck_{j}_is_used') for j in range(K)]

    r = []
    l = []
    t = []
    b = []
    for i in range(N):
        r.append(model.NewIntVar(0, max_width, f'r_{i}'))
        l.append(model.NewIntVar(0, max_width, f'l_{i}'))
        t.append(model.NewIntVar(0, max_height, f't_{i}'))
        b.append(model.NewIntVar(0, max_height, f'b_{i}'))

        model.Add(r[i] == l[i] + items[i][0]).OnlyEnforceIf(R[i].Not())
        model.Add(r[i] == l[i] + items[i][1]).OnlyEnforceIf(R[i])
        model.Add(t[i] == b[i] + items[i][1]).OnlyEnforceIf(R[i].Not())
        model.Add(t[i] == b[i] + items[i][0]).OnlyEnforceIf(R[i])

    for i in range(N):
        model.Add(sum(X[i, j] for j in range(K)) == 1)

    for i in range(N):
        for j in range(K):
            model.Add(r[i] <= trucks[j][0]).OnlyEnforceIf(X[i, j])
            model.Add(t[i] <= trucks[j][1]).OnlyEnforceIf(X[i, j])

    for i in range(N):
        for k in range(i + 1, N):
            a1 = model.NewBoolVar('a1')
            model.Add(r[i] <= l[k]).OnlyEnforceIf(a1)
            model.Add(r[i] > l[k]).OnlyEnforceIf(a1.Not())
            a2 = model.NewBoolVar('a2')
            model.Add(t[i] <= b[k]).OnlyEnforceIf(a2)
            model.Add(t[i] > b[k]).OnlyEnforceIf(a2.Not())
            a3 = model.NewBoolVar('a3')
            model.Add(r[k] <= l[i]).OnlyEnforceIf(a3)
            model.Add(r[k] > l[i]).OnlyEnforceIf(a3.Not())
            a4 = model.NewBoolVar('a4')
            model.Add(t[k] <= b[i]).OnlyEnforceIf(a4)
            model.Add(t[k] > b[i]).OnlyEnforceIf(a4.Not())

            for j in range(K):
                model.AddBoolOr([a1, a2, a3, a4]).OnlyEnforceIf([X[i, j], X[k, j]])

    for j in range(K):
        b1 = model.NewBoolVar('b')
        model.Add(sum(X[i, j] for i in range(N)) == 0).OnlyEnforceIf(b1)
        model.Add(Z[j] == 0).OnlyEnforceIf(b1)
        model.Add(sum(X[i, j] for i in range(N)) != 0).OnlyEnforceIf(b1.Not())
        model.Add(Z[j] == 1).OnlyEnforceIf(b1.Not())

    cost = sum(Z[j] * trucks[j][2] for j in range(K))
    model.Minimize(cost)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit

    start_time = time.time()
    status = solver.Solve(model)
    end_time = time.time()

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        result = []
        for i in range(N):
            item_result = [i + 1]
            for j in range(K):
                if solver.Value(X[i, j]) == 1:
                    item_result.append(j + 1)
            item_result.append(int(solver.Value(l[i])))
            item_result.append(int(solver.Value(b[i])))
            item_result.append(int(solver.Value(R[i])))
            result.append(item_result)

        num_trucks_used = int(sum(solver.Value(Z[j]) for j in range(K)))
        total_cost = solver.ObjectiveValue()
        running_time = end_time - start_time

        return result, num_trucks_used, total_cost, running_time
    else:
        return None, None, None, None


def main_solver(testcase_folder, time_limit):
    for testcase_filename in os.listdir(testcase_folder):
        testcase_path = os.path.join(testcase_folder, testcase_filename)
        data = input_data(testcase_path)
        result, num_trucks_used, total_cost, running_time = process_test_case(data, time_limit)

        if result is not None:
            print(f"Test case {testcase_filename}:")
            for item_result in result:
                print(' '.join(map(str, item_result)))
            print(f'Number of trucks used: {num_trucks_used}')
            print(f'Total cost: {total_cost}')
            print(f'Running time: {running_time:.4f} seconds')
        else:
            print(f"Test case {testcase_filename}: No feasible solution found")


if __name__ == "__main__":
    testcase_folder = 'testcase'
    time_limit = 200  # seconds
    main_solver(testcase_folder, time_limit)
