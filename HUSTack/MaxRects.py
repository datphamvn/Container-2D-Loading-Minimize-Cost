import operator
import itertools
import collections

first_item = operator.itemgetter(0)
# Sorting algos for rectangle lists
SORT_AREA  = lambda rectlist: sorted(rectlist, reverse=True, key=lambda r: r[0]*r[1])  # Sort by area
SORT_NONE = lambda rectlist: list(rectlist)  # Unsorted

class Point(object):
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "P({}, {})".format(self.x, self.y)

class Rectangle(object):
    """
    Basic rectangle primitive class.
    x, y-> Lower right corner coordinates
    """
    __slots__ = ('width', 'height', 'x', 'y', 'rid')

    def __init__(self, x, y, width, height, rid=None):
        assert (height >= 0 and width >= 0)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rid = rid

    @property
    def bottom(self):
        """
        Rectangle bottom edge y coordinate
        """
        return self.y

    @property
    def top(self):
        """
        Rectangle top edge y coordinate
        """
        return self.y + self.height

    @property
    def left(self):
        """
        Rectangle left edge x coordinate
        """
        return self.x

    @property
    def right(self):
        """
        Rectangle right edge x coordinate
        """
        return self.x + self.width

    @property
    def corner_top_l(self):
        return Point(self.left, self.top)

    @property
    def corner_top_r(self):
        return Point(self.right, self.top)

    @property
    def corner_bot_r(self):
        return Point(self.right, self.bottom)

    @property
    def corner_bot_l(self):
        return Point(self.left, self.bottom)

    def __lt__(self, other):
        """
        Compare rectangles by area (used for sorting)
        """
        return self.area() < other.area()

    def __eq__(self, other):
        """
        Equal rectangles have same area.
        """
        if not isinstance(other, self.__class__):
            return False

        return (self.width == other.width and
                self.height == other.height and
                self.x == other.x and
                self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y, self.width, self.height))

    def __iter__(self):
        """
        Iterate through rectangle corners
        """
        yield self.corner_top_l
        yield self.corner_top_r
        yield self.corner_bot_r
        yield self.corner_bot_l

    def __repr__(self):
        return "R({}, {}, {}, {})".format(self.x, self.y, self.width, self.height)

    def area(self):
        return self.width * self.height

    def contains(self, rect):
        """
        Tests if another rectangle is contained by this one

        Arguments:
            rect (Rectangle): The other rectangle

        Returns:
            bool: True if it is container, False otherwise
        """
        return (rect.y >= self.y and
                rect.x >= self.x and
                rect.y + rect.height <= self.y + self.height and
                rect.x + rect.width <= self.x + self.width)

    def intersects(self, rect, edges=False):
        """
        Detect intersections between this and another Rectangle.

        Parameters:
            rect (Rectangle): The other rectangle.
            edges (bool): True to consider rectangles touching by their
                edges or corners to be intersecting.
                (Should have been named include_touching)

        Returns:
            bool: True if the rectangles intersect, False otherwise
        """
        if edges:
            if (self.bottom > rect.top or self.top < rect.bottom or
                    self.left > rect.right or self.right < rect.left):
                return False
        else:
            if (self.bottom >= rect.top or self.top <= rect.bottom or
                    self.left >= rect.right or self.right <= rect.left):
                return False

        return True

class PackingAlgorithm(object):
    """PackingAlgorithm base class"""

    def __init__(self, width, height, rot=True, bid=None, *args, **kwargs):
        """
        Initialize packing algorithm

        Arguments:
            width (int, float): Packing surface width
            height (int, float): Packing surface height
            rot (bool): Rectangle rotation enabled or disabled
            bid (string|int|...): Packing surface identification
        """
        self.width = width
        self.height = height
        self.rot = rot
        self.rectangles = []
        self.bid = bid
        self._surface = Rectangle(0, 0, width, height)
        self.reset()

    def __len__(self):
        return len(self.rectangles)

    def __iter__(self):
        return iter(self.rectangles)

    def _fits_surface(self, width, height):
        """
        Test surface is big enough to place a rectangle

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height

        Returns:
            boolean: True if it could be placed, False otherwise
        """
        assert (width > 0 and height > 0)
        if self.rot and (width > self.width or height > self.height):
            width, height = height, width

        if width > self.width or height > self.height:
            return False
        else:
            return True

    def __getitem__(self, key):
        """
        Return rectangle in selected position.
        """
        return self.rectangles[key]

    def fitness(self, width, height, rot=False):
        """
        Metric used to rate how much space is wasted if a rectangle is placed.
        Returns a value greater or equal to zero, the smaller the value the more
        'fit' is the rectangle. If the rectangle can't be placed, returns None.

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height
            rot (bool): Enable rectangle rotation

        Returns:
            int, float: Rectangle fitness
            None: Rectangle can't be placed
        """
        raise NotImplementedError

    def add_rect(self, width, height, rid=None):
        """
        Add rectangle of width x height dimensions.

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height
            rid: Optional rectangle user id

        Returns:
            Rectangle: Rectangle with placement coordinates
            None: If the rectangle couldn't be placed.
        """
        raise NotImplementedError

    def rect_list(self):
        """
        Returns a list with all rectangles placed into the surface.

        Returns:
            List: Format [(x, y, width, height, rid), ...]
        """
        rectangle_list = []
        for r in self:
            rectangle_list.append((r.x, r.y, r.width, r.height, r.rid))

        return rectangle_list

    def validate_packing(self):
        """
        Check for collisions between rectangles, also check all are placed
        inside surface.
        """
        surface = Rectangle(0, 0, self.width, self.height)

        for r in self:
            if not surface.contains(r):
                raise Exception("Rectangle placed outside surface")

        rectangles = [r for r in self]
        if len(rectangles) <= 1:
            return

        for r1 in range(0, len(rectangles) - 2):
            for r2 in range(r1 + 1, len(rectangles) - 1):
                if rectangles[r1].intersects(rectangles[r2]):
                    raise Exception("Rectangle collision detected")

    def is_empty(self):
        # Returns true if there is no rectangles placed.
        return not bool(len(self))

    def reset(self):
        self.rectangles = []  # List of placed Rectangles.


class MaxRects(PackingAlgorithm):

    def __init__(self, width, height, rot=True, *args, **kwargs):
        super(MaxRects, self).__init__(width, height, rot, *args, **kwargs)

    def _rect_fitness(self, max_rect, width, height):
        """
        Arguments:
            max_rect (Rectangle): Destination max_rect
            width (int, float): Rectangle width
            height (int, float): Rectangle height

        Returns:
            None: Rectangle couldn't be placed into max_rect
            integer, float: fitness value
        """
        if width <= max_rect.width and height <= max_rect.height:
            return 0
        else:
            return None

    def _select_position(self, w, h):
        """
        Find max_rect with best fitness for placing a rectangle
        of dimentsions w*h

        Arguments:
            w (int, float): Rectangle width
            h (int, float): Rectangle height

        Returns:
            (rect, max_rect)
            rect (Rectangle): Placed rectangle or None if was unable.
            max_rect (Rectangle): Maximal rectangle were rect was placed
        """
        if not self._max_rects:
            return None, None

        # Normal rectangle
        fitn = ((self._rect_fitness(m, w, h), w, h, m) for m in self._max_rects
                if self._rect_fitness(m, w, h) is not None)

        # Rotated rectangle
        fitr = ((self._rect_fitness(m, h, w), h, w, m) for m in self._max_rects
                if self._rect_fitness(m, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)

        try:
            _, w, h, m = min(fit, key=first_item)
        except ValueError:
            return None, None

        return Rectangle(m.x, m.y, w, h), m

    def _generate_splits(self, m, r):
        """
        When a rectangle is placed inside a maximal rectangle, it stops being one
        and up to 4 new maximal rectangles may appear depending on the placement.
        _generate_splits calculates them.

        Arguments:
            m (Rectangle): max_rect rectangle
            r (Rectangle): rectangle placed

        Returns:
            list : list containing new maximal rectangles or an empty list
        """
        new_rects = []

        if r.left > m.left:
            new_rects.append(Rectangle(m.left, m.bottom, r.left - m.left, m.height))
        if r.right < m.right:
            new_rects.append(Rectangle(r.right, m.bottom, m.right - r.right, m.height))
        if r.top < m.top:
            new_rects.append(Rectangle(m.left, r.top, m.width, m.top - r.top))
        if r.bottom > m.bottom:
            new_rects.append(Rectangle(m.left, m.bottom, m.width, r.bottom - m.bottom))

        return new_rects

    def _split(self, rect):
        """
        Split all max_rects intersecting the rectangle rect into up to
        4 new max_rects.

        Arguments:
            rect (Rectangle): Rectangle

        Returns:
            split (Rectangle list): List of rectangles resulting from the split
        """
        max_rects = collections.deque()

        for r in self._max_rects:
            if r.intersects(rect):
                max_rects.extend(self._generate_splits(r, rect))
            else:
                max_rects.append(r)

        # Add newly generated max_rects
        self._max_rects = list(max_rects)

    def _remove_duplicates(self):
        """
        Remove every maximal rectangle contained by another one.
        """
        contained = set()
        for m1, m2 in itertools.combinations(self._max_rects, 2):
            if m1.contains(m2):
                contained.add(m2)
            elif m2.contains(m1):
                contained.add(m1)

        # Remove from max_rects
        self._max_rects = [m for m in self._max_rects if m not in contained]

    def fitness(self, width, height):
        """
        Metric used to rate how much space is wasted if a rectangle is placed.
        Returns a value greater or equal to zero, the smaller the value the more
        'fit' is the rectangle. If the rectangle can't be placed, returns None.

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height

        Returns:
            int, float: Rectangle fitness
            None: Rectangle can't be placed
        """
        assert (width > 0 and height > 0)

        rect, max_rect = self._select_position(width, height)
        if rect is None:
            return None

        # Return fitness
        return self._rect_fitness(max_rect, rect.width, rect.height)

    def add_rect(self, width, height, rid=None):
        """
        Add rectangle of widthxheight dimensions.

        Arguments:
            width (int, float): Rectangle width
            height (int, float): Rectangle height
            rid: Optional rectangle user id

        Returns:
            Rectangle: Rectangle with placemente coordinates
            None: If the rectangle couldn be placed.
        """
        assert (width > 0 and height > 0)

        # Search best position and orientation
        rect, _ = self._select_position(width, height)
        if not rect:
            return None

        # Subdivide all the max rectangles intersecting with the selected
        # rectangle.
        self._split(rect)

        # Remove any max_rect contained by another
        self._remove_duplicates()

        # Store and return rectangle position.
        rect.rid = rid
        self.rectangles.append(rect)
        return rect

    def reset(self):
        super(MaxRects, self).reset()
        self._max_rects = [Rectangle(0, 0, self.width, self.height)]


class MaxRectsBl(MaxRects):

    def _select_position(self, w, h):
        """
        Select the position where the y coordinate of the top of the rectangle
        is lower, if there are severtal pick the one with the smallest x
        coordinate
        """
        fitn = ((m.y + h, m.x, w, h, m) for m in self._max_rects
                if self._rect_fitness(m, w, h) is not None)
        fitr = ((m.y + w, m.x, h, w, m) for m in self._max_rects
                if self._rect_fitness(m, h, w) is not None)

        if not self.rot:
            fitr = []

        fit = itertools.chain(fitn, fitr)

        try:
            _, _, w, h, m = min(fit, key=first_item)
        except ValueError:
            return None, None

        return Rectangle(m.x, m.y, w, h), m


class MaxRectsBssf(MaxRects):
    """Best Sort Side Fit minimize short leftover side"""

    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return min(max_rect.width - width, max_rect.height - height)


class MaxRectsBaf(MaxRects):
    """Best Area Fit pick maximal rectangle with smallest area
    where the rectangle can be placed"""

    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return (max_rect.width * max_rect.height) - (width * height)


class MaxRectsBlsf(MaxRects):
    """Best Long Side Fit minimize long leftover side"""

    def _rect_fitness(self, max_rect, width, height):
        if width > max_rect.width or height > max_rect.height:
            return None

        return max(max_rect.width - width, max_rect.height - height)

class BinFactory(object):

    def __init__(self, width, height, cost, count, pack_algo, *args, **kwargs):
        self._width = width
        self._height = height
        self._count = count
        self._cost = cost

        self._pack_algo = pack_algo
        self._algo_kwargs = kwargs
        self._algo_args = args
        self._ref_bin = None  # Reference bin used to calculate fitness

        self._bid = kwargs.get("bid", None)

    def _create_bin(self):
        return self._pack_algo(self._width, self._height, *self._algo_args, **self._algo_kwargs)

    def is_empty(self):
        return self._count < 1

    def fitness(self, width, height):
        if not self._ref_bin:
            self._ref_bin = self._create_bin()

        return self._ref_bin.fitness(width, height)

    def fits_inside(self, width, height):
        # Determine if rectangle width x height will fit into empty bin
        if not self._ref_bin:
            self._ref_bin = self._create_bin()

        return self._ref_bin._fits_surface(width, height)

    def new_bin(self):
        if self._count > 0:
            self._count -= 1
            return self._create_bin()
        else:
            return None

    def __eq__(self, other):
        return (self._width, self._height, self._cost) == (other._width, other._height, other._cost)

    def __lt__(self, other):
        return (self._cost, self._width * self._height) < (other._cost, other._width * other._height)

    def __str__(self):
        return f"Bin: {self._width}x{self._height}, Count: {self._count}, Cost: {self._cost}, ID: {self._bid}"


class PackerBFFMixin(object):
    """
    BFF (Bin First Fit): Pack rectangle in first bin it fits
    """
    def add_rect(self, width, height, rid=None):
        # see if this rect will fit in any of the open bins
        for b in self._open_bins:
            rect = b.add_rect(width, height, rid=rid)
            if rect is not None:
                return rect

        while True:
            # can we find an unopened bin that will hold this rect?
            new_bin = self._new_open_bin(width, height, rid=rid)
            if new_bin is None:
                return None

            # _new_open_bin may return a bin that's too small,
            # so we have to double-check
            rect = new_bin.add_rect(width, height, rid=rid)
            if rect is not None:
                return rect


class PackerMaster(object):
    """
    Rectangles are packed as soon are they are added
    """

    def __init__(self, pack_algo=MaxRectsBssf, rotation=True):
        """
        Arguments:
            pack_algo (PackingAlgorithm): What packing algo to use
            rotation (bool): Enable/Disable rectangle rotation
        """
        self._rotation = rotation
        self._pack_algo = pack_algo
        self.reset()

    def __iter__(self):
        return itertools.chain(self._closed_bins, self._open_bins)

    def __len__(self):
        return len(self._closed_bins) + len(self._open_bins)

    def __getitem__(self, key):
        """
        Return bin in selected position. (excluding empty bins)
        """
        if not isinstance(key, int):
            raise TypeError("Indices must be integers")

        size = len(self)  # avoid recalulations

        if key < 0:
            key += size

        if not 0 <= key < size:
            raise IndexError("Index out of range")

        if key < len(self._closed_bins):
            return self._closed_bins[key]
        else:
            return self._open_bins[key - len(self._closed_bins)]

    def _new_open_bin(self, width=None, height=None, rid=None):
        """
        Extract the next empty bin and append it to open bins

        Returns:
            PackingAlgorithm: Initialized empty packing bin.
            None: No bin big enough for the rectangle was found
        """
        factories_to_delete = set()  #
        new_bin = None

        for key, binfac in self._empty_bins.items():

            # Only return the new bin if the rect fits.
            # (If width or height is None, caller doesn't know the size.)
            if not binfac.fits_inside(width, height):
                continue

            # Create bin and add to open_bins
            new_bin = binfac.new_bin()
            if new_bin is None:
                continue
            self._open_bins.append(new_bin)

            # If the factory was depleted mark for deletion
            if binfac.is_empty():
                factories_to_delete.add(key)

            break

        # Delete marked factories
        for f in factories_to_delete:
            del self._empty_bins[f]

        return new_bin

    def add_bin(self, width, height, cost, count=1, **kwargs):
        # accept the same parameters as PackingAlgorithm objects
        kwargs['rot'] = self._rotation
        bin_factory = BinFactory(width, height, cost, count, self._pack_algo, **kwargs)
        self._empty_bins[next(self._bin_count)] = bin_factory

    def rect_list(self):
        rectangles = []
        bin_count = 0

        for abin in self:
            for rect in abin:
                rectangles.append((bin_count, rect.x, rect.y, rect.width, rect.height, rect.rid))
            bin_count += 1

        return rectangles

    def bin_list(self):
        """
        Return a list of the dimmensions of the bins in use, that is closed
        or open containing at least one rectangle
        """
        return [(b.width, b.height, b.bid) for b in self if b]

    def validate_packing(self):
        for b in self:
            b.validate_packing()

    def reset(self):
        # Bins fully packed and closed.
        self._closed_bins = collections.deque()

        # Bins ready to pack rectangles
        self._open_bins = collections.deque()

        # User provided bins not in current use
        self._empty_bins = collections.OrderedDict()  # O(1) deletion of arbitrary elem
        self._bin_count = itertools.count()


class Packer(PackerMaster):
    """
    Rectangles aren't packed untils pack() is called
    """

    def __init__(self, pack_algo=MaxRectsBssf, sort_algo=SORT_NONE, rotation=True):
        super(Packer, self).__init__(pack_algo=pack_algo, rotation=rotation)

        self._sort_algo = sort_algo

        # User provided bins and Rectangles
        self._avail_bins = collections.deque()
        self._avail_rect = collections.deque()

        # Aux vars used during packing
        self._sorted_rect = []

    def add_bin(self, width, height, cost, count=1, **kwargs):
        self._avail_bins.append((width, height, cost, count, kwargs))

    def add_rect(self, width, height, rid=None):
        self._avail_rect.append((width, height, rid))

    def _is_everything_ready(self):
        return self._avail_rect and self._avail_bins

    def pack(self):

        self.reset()

        if not self._is_everything_ready():
            # maybe we should throw an error here?
            return

        # Add available bins to packer
        for b in self._avail_bins:
            width, height, cost, count, extra_kwargs = b
            super(Packer, self).add_bin(width, height, cost, count, **extra_kwargs)

        # If enabled sort rectangles
        self._sorted_rect = self._sort_algo(self._avail_rect)

        # Start packing
        for r in self._sorted_rect:
            super(Packer, self).add_rect(*r)


class PackerBFF(Packer, PackerBFFMixin):
    """
    BFF (Bin First Fit): Pack rectangle in first bin it fits
    """
    pass


def newPacker(bin_algo="BFF", pack_algo=MaxRectsBl, sort_algo=SORT_NONE, rotation=True):
    """
    Packer factory helper function

    Arguments:
        bin_algo (PackingBin): Bin selection heuristic
        pack_algo (PackingAlgorithm): Algorithm used
        sort_algo (SortItems): Choose criteria to sort items
        rotation (boolean): Enable or disable rectangle rotation.

    Returns:
        Packer: Initialized packer instance.
    """
    if bin_algo == "BFF":
        packer_class = PackerBFF
    else:
        raise AttributeError("Unsupported bin selection heuristic")

    if sort_algo:
        return packer_class(pack_algo=pack_algo, sort_algo=sort_algo, rotation=rotation)
    else:
        return packer_class(pack_algo=pack_algo, rotation=rotation)

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

# Input
N, K = map(int, input().split())  # Number of items and trucks
items = [tuple(map(int, input().split())) + (i+1,) for i in range(N)]  # List of item dimensions (w, l) with indices
trucks = [tuple(map(int, input().split())) + (i+1,) for i in range(N)]  # List of truck dimensions (W, L, cost) with indices


# Initialize Packer
packer = newPacker(bin_algo="BFF", sort_algo=SORT_AREA, pack_algo=MaxRectsBl)

# Add items to the packing queue
for item in items:
    packer.add_rect(item[0], item[1], rid=item[2])

# Add bins (trucks) where the items will be placed
trucks = sort_trucks_by_effectiveness(trucks, items)
for truck in trucks:
    packer.add_bin(*truck[:3], bid=truck[3])

# Start packing
packer.pack()

packed_items = packer.rect_list()
packed_bins = packer.bin_list()
packed_items_sorted = sorted(packed_items, key=lambda x: x[5])

# Output sorted by rid
for rect in packed_items_sorted:
    b, x, y, w, h, rid = rect
    # Determine if the item was rotated (0 if no rotation, 1 if rotated)
    original_w, original_l = next((item[0], item[1]) for item in items if item[2] == rid)
    rotation = 1 if (w, h) != (original_w, original_l) else 0
    print(rid, packed_bins[b][2], x, y, rotation)
