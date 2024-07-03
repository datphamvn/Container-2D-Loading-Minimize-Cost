import os
import time
import argparse
from C2DLMC import *

# Default pack algorithm
DEFAULT_PACK_ALGO = MaxRectsBaf

def sort_trucks_by_effectiveness(trucks, items):
    total_item_area = sum(w * l for w, l, _ in items)

    trucks_with_ratio = []
    for truck in trucks:
        W, L, c, truck_id = truck
        truck_area = W * L
        fit_ratio = min(total_item_area, truck_area) / truck_area
        cost_effectiveness = truck_area / c
        adjusted_ratio = fit_ratio * cost_effectiveness
        trucks_with_ratio.append((truck, adjusted_ratio))

    trucks_sorted = sorted(trucks_with_ratio, key=lambda x: x[1], reverse=True)

    return [truck for truck, _ in trucks_sorted]


def process_test_case(testcase_path, pack_algo):
    with open(testcase_path, 'r') as f:
        lines = f.readlines()

    N, K = map(int, lines[0].split())  # Number of items and trucks
    items = [tuple(map(int, line.split())) + (i + 1,) for i, line in enumerate(lines[1:N + 1])]
    trucks = [tuple(map(int, line.split())) + (i + 1,) for i, line in enumerate(lines[N + 1:N + 1 + K])]

    # Initialize Packer
    packer = newPacker(bin_algo="BFF", sort_algo=SORT_AREA, pack_algo=pack_algo)

    # Add items to the packing queue
    for item in items:
        packer.add_rect(item[0], item[1], rid=item[2])

    # Add bins (trucks) where the items will be placed
    trucks = sort_trucks_by_effectiveness(trucks, items)
    for truck in trucks:
        packer.add_bin(*truck[:3], bid=truck[3])

    # Start packing
    start_time = time.time()
    packer.pack()
    end_time = time.time()

    packed_items = packer.rect_list()
    packed_bins = packer.bin_list()

    total_cost = sum(truck[2] for truck in trucks if any(p[0] == trucks.index(truck) for p in packed_items))
    total_time = end_time - start_time

    return total_cost, total_time


def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Process test cases with a specified packing algorithm.")
    parser.add_argument('--pack_algo', type=str, default='MaxRectsBaf', help='Packing algorithm to use')
    parser.add_argument('--testcase_folder', type=str, default='testcase', help='Folder containing test cases')
    args = parser.parse_args()

    # Map string argument to actual algorithm
    pack_algo_mapping = {
        'SkylineBl': SkylineBl,
        'MaxRectsBl': MaxRectsBl,
        'MaxRectsBaf': MaxRectsBaf,
        'MaxRectsBssf': MaxRectsBssf,
        'MaxRectsBlsf': MaxRectsBlsf,
        'GuillotineBafMaxas': GuillotineBafMaxas
    }

    pack_algo = pack_algo_mapping.get(args.pack_algo, DEFAULT_PACK_ALGO)

    # Process each test case in the folder
    for testcase_filename in os.listdir(args.testcase_folder):
        testcase_path = os.path.join(args.testcase_folder, testcase_filename)
        total_cost, total_time = process_test_case(testcase_path, pack_algo)
        print(f"Test case {testcase_filename}: Total cost = {total_cost}, Time to run = {total_time:.4f} seconds")


if __name__ == "__main__":
    main()
