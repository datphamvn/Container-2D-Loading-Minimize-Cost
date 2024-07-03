
# Container 2D Loading Minimize Cost

## Problem
`K` trucks `1, 2, ..., K` are available for transporting `N` packages `1, 2, ..., N`. Each truck `k` has a container size of `Wk x Hk`. The dimensions of each package `i` are `wi x hi`. Packages that are placed in the same container must not overlap. Assume that the number K can be large, leading to a great number of trucks that are not being used. `Ck` represents the cost of using truck `k`. Find a solution that loads all the packages into those given trucks such that **the total cost of trucks used is minimal**.

## Installation
```commandline
pip install -r requirements.txt
```

## Project Folder Structure
```
>--HUSTack
|   >--CP.py
|   >--MIP.py
|   >--MaxRects.py
|   >--branchAndBound.cpp
|   >--guillotine.cpp
>--C2DLMC
|   >--__init__.py
|   >--geometry.py
|   >--guillotine.py
|   >--maxrects.py
|   >--pack_algo.py
|   >--packer.py
|   >--skyline.py
>--testcase
|   >--test01.txt
|   >--test02.txt
|   >--test03.txt
|   >--test04.txt
|   >--test05.txt
|   >--test06.txt
|   >--test07.txt
|   >--test08.txt
|   >--test09.txt
|   >--test10.txt
>--CP.py
>--MIP.py
>--branchAndBound.py
>--heuristic.py
>--requirements.txt
```

- The `HUSTack` folder contains code from members as described in the "Our team" section.
- The `C2DLMC` folder contains helpers for 3 heuristic algorithms: Guillotine, Maximal Rectangle, and Skyline.
- The `testcase` folder contains the experimental evaluation dataset.
- The files `CP.py`, `MIP.py`, `branchAndBound.py`, and `heuristic.py` are used to execute all test sets in the `testcase` folder.

## How to Run Heuristic Algorithms
The heuristic algorithms include 3 groups of algorithms and their variants:

### 1. **Guillotine Algorithm**
The Guillotine algorithm divides the space into smaller rectangles using a recursive process, similar to a guillotine cut. The primary goal is to minimize the area wasted and maximize the area used for placing items. Here is the variant explained:

- **GuillotineBafMaxas**:
  - **Baf** (Best Area Fit): Selects the rectangle that fits the best in terms of area, minimizing wasted space.
  - **Maxas** (Maximize Area Savings): Focuses on saving the maximum area for future rectangles, ensuring better utilization of the remaining space.

### 2. **MaxRects Algorithm**
The MaxRects algorithm maintains a list of free rectangles and places new rectangles by choosing the best-fit position according to a specific strategy. This method is versatile and adapts to different packing needs. The variants are:

- **MaxRectsBl** (Best Long Side Fit):
  - Chooses the position where the longer side of the rectangle fits best in the available free space.

- **MaxRectsBaf** (Best Area Fit):
  - Selects the position that minimizes the remaining free area after placing the rectangle, ensuring minimal wastage.

- **MaxRectsBssf** (Best Short Side Fit):
  - Chooses the position where the shorter side of the rectangle fits best in the available free space.

- **MaxRectsBlsf** (Bottom-Left Strategy Fit):
  - Uses a bottom-left strategy, where the rectangle is placed as close as possible to the bottom-left corner of the available space.

### 3. **Skyline Algorithm**
The Skyline algorithm builds a "skyline" of filled rectangles and places new rectangles by choosing the lowest available position that fits. This algorithm is particularly efficient for height-based bin packing problems. Here is the variant explained:

- **SkylineBl**:
  - Uses a bottom-left strategy, where the rectangle is placed as close as possible to the bottom-left corner of the available space, ensuring minimal vertical gaps and efficient stacking.

To run the algorithm, use the command:
```commandline
python heuristic.py --pack_algo <algo>
```

- Guillotine: GuillotineBafMaxas
- MaxRectsBl: MaxRectsBl, MaxRectsBaf, MaxRectsBssf, MaxRectsBlsf,
- Skyline: SkylineBl 

## Our Team

| Member                | Student ID | Tasks                                                                                                                                                    |
|-----------------------|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phạm Vũ Tuấn Đạt      | 20210158   | - Maximal Rectangle Algorithm (heuristic) <br> - Skyline Algorithm (heuristic) <br> - Branch and Bound - Python <br> - Experiments, slides, report writing |
| Nông Thanh Huy        | 20204567   | - Mixed-Integer Programming <br> - Slides, report writing                                                                                                |
| Nguyễn Như Phước      | 20204597   | - Constraint Programming <br> - Slides, report writing                                                                                                    |
| Nguyễn Văn Thọ        | 20204694   | - Guillotine Algorithm (heuristic) <br> - Branch and Bound <br> - Slides, report writing                                                                  |
