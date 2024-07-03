import os
import time
import sys

# Constants
MAX_N = 1000
MAX_K = 1000

# Function to check if item i can be placed in truck k
def canPlace(i, k, x, y, o, w, l, W, L, result_t, result_x, result_y, result_o):
    if (x + w[i] * (1 - o) + l[i] * o) > W[k] or (y + w[i] * o + l[i] * (1 - o)) > L[k]:
        return False

    for j in range(i):
        if result_t[j] == k and not (
            x + w[i] * (1 - o) + l[i] * o <= result_x[j] or
            result_x[j] + w[j] * (1 - o) + l[j] * o <= x or
            y + w[i] * o + l[i] * (1 - o) <= result_y[j] or
            result_y[j] + w[j] * o + l[j] * (1 - o) <= y):
            return False
    return True

# Function to calculate total cost
def calcCost(K, c, used):
    totalCost = 0
    for j in range(K):
        if used[j] > 0:
            totalCost += c[j]
    return totalCost

# Backtracking function
def Try(i, N, K, w, l, W, L, c, result_t, result_x, result_y, result_o, solution_t, solution_x, solution_y, solution_o, used, min_cost):
    if i == N:
        tmp = calcCost(K, c, used)
        if tmp < min_cost[0]:
            min_cost[0] = tmp
            for j in range(N):
                solution_t[j] = result_t[j]
                solution_x[j] = result_x[j]
                solution_y[j] = result_y[j]
                solution_o[j] = result_o[j]
        return

    for k in range(K):
        for x in range(0, W[k] - w[i] + 1, 10):
            for y in range(0, L[k] - l[i] + 1, 10):
                for o in range(2):
                    if canPlace(i, k, x, y, o, w, l, W, L, result_t, result_x, result_y, result_o):
                        used[k] += 1
                        result_t[i] = k
                        result_x[i] = x
                        result_y[i] = y
                        result_o[i] = o
                        if calcCost(K, c, used) < min_cost[0]:
                            Try(i + 1, N, K, w, l, W, L, c, result_t, result_x, result_y, result_o, solution_t, solution_x, solution_y, solution_o, used, min_cost)
                        used[k] -= 1

# Function to process a single test case
def process_test_case(testcase_path):
    with open(testcase_path, 'r') as f:
        lines = f.readlines()

    N, K = map(int, lines[0].split())
    w = [0] * N
    l = [0] * N
    W = [0] * K
    L = [0] * K
    c = [0] * K

    for i in range(N):
        w[i], l[i] = map(int, lines[1 + i].split())

    for k in range(K):
        W[k], L[k], c[k] = map(int, lines[1 + N + k].split())

    result_t = [-1] * N
    result_x = [0] * N
    result_y = [0] * N
    result_o = [0] * N

    solution_t = [-1] * N
    solution_x = [0] * N
    solution_y = [0] * N
    solution_o = [0] * N

    used = [0] * K
    min_cost = [sys.maxsize]

    start_time = time.time()
    Try(0, N, K, w, l, W, L, c, result_t, result_x, result_y, result_o, solution_t, solution_x, solution_y, solution_o, used, min_cost)
    end_time = time.time()

    total_cost = min_cost[0]
    total_time = end_time - start_time

    # Print result
    print(f"Test case {testcase_path}: Total cost = {total_cost}, Time to run = {total_time:.4f} seconds")
    for j in range(N):
        print(f"{j + 1} {solution_t[j] + 1} {solution_x[j]} {solution_y[j]} {solution_o[j]}")

# Directory containing test cases
testcase_folder = 'testcase'

# Process each test case in the folder
for testcase_filename in os.listdir(testcase_folder):
    testcase_path = os.path.join(testcase_folder, testcase_filename)
    process_test_case(testcase_path)
