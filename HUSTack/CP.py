from ortools.sat.python import cp_model

def main_solver(time_limit):
    # Nhập số lượng mặt hàng và số lượng xe
    N, K = map(int, input().split())  # số mặt hàng, số thùng

    # Nhập thông tin các mặt hàng
    items = []

    # Nhập kích thước của từng mặt hàng
    for _ in range(N):
        w, h = map(int, input().split())
        items.append((w, h))

    # Nhập thông tin các xe
    trucks = []

    # Nhập kích thước và chi phí của từng thùng
    for _ in range(K):
        w, h, c = map(int, input().split())
        trucks.append((w, h, c))

    max_width = max(x[0] for x in trucks)
    max_height = max(x[1] for x in trucks)

    # Tạo mô hình
    model = cp_model.CpModel()

    # Biến quyết định
    X = {}
    R = []
    for i in range(N):
        # R[i] = 1 nếu mặt hàng i được quay 90 độ
        R.append(model.NewBoolVar(f'item_{i}_rotated'))
        for j in range(K):
            # X[i, j] = 1 iff item i is packed in bin j.
            X[i, j] = model.NewBoolVar(f'item_{i}_in_truck_{j}')

    # Z[j] = 1 nếu xe j được sử dụng
    Z = [model.NewBoolVar(f'truck_{j}_is_used)') for j in range(K)]

    # Coordinate
    r = []  # right coordinate
    l = []  # left coordinate
    t = []  # top coordinate
    b = []  # bottom coordinate
    for i in range(N):
        r.append(model.NewIntVar(0, max_width, f'r_{i}'))
        l.append(model.NewIntVar(0, max_width, f'l_{i}'))
        t.append(model.NewIntVar(0, max_height, f't_{i}'))
        b.append(model.NewIntVar(0, max_height, f'b_{i}'))

        # Nếu mặt hàng được xoay -> thay đổi tọa độ hiện tại
        model.Add(r[i] == l[i] + items[i][0]).OnlyEnforceIf(R[i].Not())
        model.Add(r[i] == l[i] + items[i][1]).OnlyEnforceIf(R[i])
        model.Add(t[i] == b[i] + items[i][1]).OnlyEnforceIf(R[i].Not())
        model.Add(t[i] == b[i] + items[i][0]).OnlyEnforceIf(R[i])

    # Ràng buộc
    # Mỗi mặt hàng được chất lên 1 xe duy nhất
    for i in range(N):
        model.Add(sum(X[i, j] for j in range(K)) == 1)

    # Nếu mặt hàng được đặt trên xe thì kích thước mặt hàng không được vượt quá kích thước xe
    for i in range(N):
        for j in range(K):
            model.Add(r[i] <= trucks[j][0]).OnlyEnforceIf(X[i, j])
            model.Add(t[i] <= trucks[j][1]).OnlyEnforceIf(X[i, j])

    # Nếu 2 mặt hàng cùng được đặt chung xe thì chúng không được chồng lên nhau
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
                model.AddBoolOr(a1, a2, a3, a4).OnlyEnforceIf(X[i, j], X[k, j])

    # Tìm những xe được sử dụng
    for j in range(K):
        b1 = model.NewBoolVar('b')
        model.Add(sum(X[i, j] for i in range(N)) == 0).OnlyEnforceIf(b1)
        model.Add(Z[j] == 0).OnlyEnforceIf(b1)
        model.Add(sum(X[i, j] for i in range(N)) != 0).OnlyEnforceIf(b1.Not())
        model.Add(Z[j] == 1).OnlyEnforceIf(b1.Not())

    # Hàm mục tiêu
    cost = sum(Z[j] * trucks[j][2] for j in range(K))
    model.Minimize(cost)

    # Tạo bộ giải và giải mô hình
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)

    # Kết quả
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for i in range(N):
            if solver.Value(R[i]) == 1:
                print(f'Rotate item {i + 1} and put', end=' ')
            else:
                print(f'Put item {i + 1}', end=' ')
            for j in range(K):
                if solver.Value(X[i, j]) == 1:
                    print(f'in truck {j + 1}', end=' ')
            print(f'that the top right corner coordinate (x, y) is ({solver.Value(r[i])}, {solver.Value(t[i])})')

        print(f'Số xe được sử dụng  : {sum(solver.Value(Z[i]) for i in range(K))}')
        print(f'Tổng chi phí         : {solver.ObjectiveValue()}')
        print(f'Thời gian       : {solver.UserTime()}')

    else:
        print('NO SOLUTIONS')


if __name__ == "__main__":
    main_solver(200)
