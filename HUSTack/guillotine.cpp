#include <algorithm>
#include <climits>
#include <iostream>
#include <vector>

using namespace std;

/*----------------- DECLARE CONSTANTS -----------------*/
const int MAXN = 1e4 + 7;
const int EPS = 1e-8;
const int INF = INT_MAX;

/*----------------- DECLARE STRUCTURES -----------------*/
struct Item {
    int id;
    int width, height, corner_x, corner_y; // corner_x, corner_y: the bottom-left corner of the item
    int pos_bin;                           // Position of the bin that the item is inserted
    bool rotated = false;

    void rotate() {
        rotated = !rotated;
        swap(width, height);
    }
};

struct FreeRectangle {
    int corner_x, corner_y, width, height;

    bool can_contain(const Item &item, bool is_rotated) const {
        if (is_rotated) {
            if ((item.width <= height) && (item.height <= width))
                return true;
        } else {
            if ((item.width <= width) && (item.height <= height))
                return true;
        }
        return false;
    }

    bool operator==(const FreeRectangle &x) const {
        return (corner_x == x.corner_x) &&
               (corner_y == x.corner_y) &&
               (width == x.width) &&
               (height == x.height);
    }
};

struct Bin {
    int id;
    int width, height, cost;
    vector<FreeRectangle> list_of_free_rec;
    vector<Item> list_of_items;

    void add_item(Item &item, bool rotated, int x, int y) {
        if (rotated)
            item.rotate();
        item.corner_x = x;
        item.corner_y = y;
        list_of_items.push_back(item);
    }
};

struct RankingFreeRecResult {
    FreeRectangle rec; // The free_rec that the item can be inserted
    unsigned int pos;  // Position of the free_rec in the list of free_rec of a bin
    bool rotated;      // Check if the item is rotated
    bool exist;        // Check if the item can be inserted to the bin

    RankingFreeRecResult() {
        pos = 0;
        rotated = exist = 0;
    }
};

struct BestShortSideScorer { // Define scoring for the pair of free_rec and item
    int short_side, long_side;

    BestShortSideScorer() {
        short_side = long_side = INF;
    }

    BestShortSideScorer(FreeRectangle _rec, Item _item, bool _rotated) {
        int remaining_width, remaining_height;
        if (!_rotated) {
            remaining_width = _rec.width - _item.width;
            remaining_height = _rec.height - _item.height;
        } else {
            remaining_width = _rec.width - _item.height;
            remaining_height = _rec.height - _item.width;
        }
        short_side = min(remaining_width, remaining_height);
        long_side = max(remaining_width, remaining_height);
    }

    // overload comparison operator
    bool operator<(const BestShortSideScorer &other) const {
        if (short_side == other.short_side)
            return long_side < other.long_side;
        return short_side < other.short_side;
    }

    // overload assignment operator
    BestShortSideScorer operator()(BestShortSideScorer other) {
        short_side = other.short_side;
        long_side = other.long_side;
        return *this;
    }
};

/*----------------- DECLARE GLOBAL VARIABLES -----------------*/
int n_items, n_bins;
Item items[MAXN];
Bin bins[MAXN];

/*----------------- DECLARE FUNCTIONS -----------------*/
bool compare_item_by_longer_side(Item a, Item b) {
    if (a.height == b.height)
        return a.width > b.width;
    return a.height > b.height;
}

bool compare_item_by_id(Item a, Item b) {
    return a.id < b.id;
}

bool compare_bin_by_density(Bin a, Bin b) {
    float value_a = (a.width * a.height)/(a.cost);
    float value_b = (b.width * b.height)/(b.cost);
    if(value_a == value_b)
        return (a.width * a.height)/(a.width + a.height) > (b.width * b.height)/(b.width + b.height);
    return value_a > value_b;
}

// Find best free_rec for the item in the list free_rec of a bin
RankingFreeRecResult best_ranking(Bin bin, Item item) {
    RankingFreeRecResult ans_return;
    BestShortSideScorer best_score;

    // Loop to find the best score
    for (unsigned int i = 0; i < bin.list_of_free_rec.size(); ++i) {
        FreeRectangle rec = bin.list_of_free_rec[i];

        BestShortSideScorer score_rec(rec, item, false);
        // Not rotate case
        if (rec.can_contain(item, false) && score_rec < best_score) {
            best_score = score_rec;
            ans_return.rec = rec;
            ans_return.pos = i;
            ans_return.rotated = 0;
            ans_return.exist = 1;
        }
        // Rotate case
        score_rec = BestShortSideScorer(rec, item, true);
        if (rec.can_contain(item, true) && score_rec < best_score) {
            best_score = score_rec;
            ans_return.rec = rec;
            ans_return.pos = i;
            ans_return.rotated = 1;
            ans_return.exist = 1;
        }
    }

    return ans_return;
}

// Split initial free_rec after having an insertion
vector<FreeRectangle> spliting_process_guillotine(bool horizontal, FreeRectangle rec, Item item) {
    vector<FreeRectangle> list_of_free_rec;
    FreeRectangle new_free_rec;

    int right_x = rec.corner_x + item.width,
        right_y = rec.corner_y,
        right_width = rec.width - item.width,
        top_x = rec.corner_x,
        top_y = rec.corner_y + item.height,
        top_height = rec.height - item.height;

    int right_height = (horizontal) ? item.height : rec.height;
    int top_width = (horizontal) ? rec.width : item.width;
    if ((right_width > 0) & (right_height > 0)) {
        new_free_rec.corner_x = right_x;
        new_free_rec.corner_y = right_y;
        new_free_rec.width = right_width;
        new_free_rec.height = right_height;
        list_of_free_rec.push_back(new_free_rec);
    }
    if ((top_width > 0) & (top_height > 0)) {
        new_free_rec.corner_x = top_x;
        new_free_rec.corner_y = top_y;
        new_free_rec.width = top_width;
        new_free_rec.height = top_height;
        list_of_free_rec.push_back(new_free_rec);
    }
    return list_of_free_rec;
}

vector<FreeRectangle> spliting_guillotine(FreeRectangle rec, Item item) {
    // Split by Shorter Axis: split on the horizontal axis if rec.width <= rec.height
    return spliting_process_guillotine(rec.width <= rec.height, rec, item);
}

// Merge two initial free_recs into a larger free_rec if possible
void merge_free_recs(Bin &bin) {
    vector<FreeRectangle> match_width, match_height;

    for (unsigned int i = 0; i < bin.list_of_free_rec.size(); ++i) {
        FreeRectangle first = bin.list_of_free_rec[i];
        bool check_exist_width = 0;
        bool check_exist_height = 0;
        unsigned int pos_check_width = 0;
        unsigned int pos_check_height = 0;
        // Find the mergable free_rec with the same width or height
        for (unsigned int j = 0; j < bin.list_of_free_rec.size(); ++j) {
            FreeRectangle second = bin.list_of_free_rec[j];
            if (j == i)
                continue;
            // Find the mergable free_rec with the same width
            if ((first.width == second.width) && (first.corner_x == second.corner_x) && (second.corner_y == first.corner_y + first.height)) {
                check_exist_width = 1;
                pos_check_width = j;
                break;
            }
            // Find the mergable free_rec with the same height
            if ((first.height == second.height) && (first.corner_y == second.corner_y) && (second.corner_x == first.corner_x + first.width)) {
                check_exist_height = 1;
                pos_check_height = j;
                break;
            }
        }
        // Merge two free_rec with the same width
        if (check_exist_width) {
            FreeRectangle merged_rec;
            merged_rec.width = first.width;
            merged_rec.height = first.height + bin.list_of_free_rec[pos_check_width].height;
            merged_rec.corner_x = first.corner_x;
            merged_rec.corner_y = first.corner_y;
            // Remove the two initial free_recs
            bin.list_of_free_rec.erase(bin.list_of_free_rec.begin() + pos_check_width);
            if (pos_check_width < i)
                --i;
            bin.list_of_free_rec.erase(bin.list_of_free_rec.begin() + i);
            --i;
            // Add the merged free_rec
            bin.list_of_free_rec.push_back(merged_rec);
        }

        // Merge two free_rec with the same height
        if (check_exist_height) {
            FreeRectangle merged_rec;
            merged_rec.width = first.width + bin.list_of_free_rec[pos_check_height].width;
            merged_rec.height = first.height;
            merged_rec.corner_x = first.corner_x;
            merged_rec.corner_y = first.corner_y;
            // Remove the two initial free_recs
            bin.list_of_free_rec.erase(bin.list_of_free_rec.begin() + pos_check_height);
            if (pos_check_height < i)
                --i;
            bin.list_of_free_rec.erase(bin.list_of_free_rec.begin() + i);
            --i;
            // Add the merged free_rec
            bin.list_of_free_rec.push_back(merged_rec);
        }
    }
}

// Check if item find a possible free_rec in the bin for inserting process
bool insert_item_to_bin(Bin &bin, Item &item) {
    RankingFreeRecResult ranking_result = best_ranking(bin, item);

    if (!ranking_result.exist)
        return false;

    item.pos_bin = bin.id;
    FreeRectangle best_rec = ranking_result.rec;
    unsigned int best_pos = ranking_result.pos;
    int rotated = ranking_result.rotated;

    bin.add_item(item, rotated, best_rec.corner_x, best_rec.corner_y);

    // Replace the best_rec with the new free_recs after inserting the item
    bin.list_of_free_rec.erase(bin.list_of_free_rec.begin() + best_pos);
    vector<FreeRectangle> new_rec = spliting_guillotine(best_rec, item);
    for (auto rec : new_rec) {
        bin.list_of_free_rec.push_back(rec);
    }

    // Merge the free_rec if possible
    merge_free_recs(bin);

    return true;
}

/*----------------- MAIN PROGRAM ------------------*/
/*----------------- READ INPUT -----------------*/
void read_input() {
    cin >> n_items >> n_bins;
    for (int i = 1; i <= n_items; ++i) {
        cin >> items[i].width >> items[i].height;
        items[i].id = i;
        // Set all items to have the longer side on the width
        if (items[i].width > items[i].height)
            items[i].rotate();
    }

    // Read and prepare for the list of bins
    for (int j = 1; j <= n_bins; ++j) {
        cin >> bins[j].width >> bins[j].height >> bins[j].cost;
        bins[j].id = j;
        // The bin is a free rectangle itself at the beginning
        FreeRectangle first_rec;
        first_rec.width = bins[j].width;
        first_rec.height = bins[j].height;
        first_rec.corner_x = first_rec.corner_y = 0;
        bins[j].list_of_free_rec.push_back(first_rec);
    }

    sort(items + 1, items + n_items + 1, compare_item_by_longer_side);
    sort(bins + 1, bins + n_bins + 1, compare_bin_by_density);
}

/*----------------- SOLVE -----------------*/
void solve_problem() {
    for (int i = 1; i <= n_items; ++i) {
        for (int j = 1; j <= n_bins; ++j) // greedy bin selection, choose the first bin that can contain the item
            if (insert_item_to_bin(bins[j], items[i]))
                break;
    }
}

/*----------------- PRINT SOLUTION -----------------*/
void print_solution() {
    sort(items + 1, items + n_items + 1, compare_item_by_id);
    for (int i = 1; i <= n_items; ++i) {
        cout << items[i].id << " " << items[i].pos_bin << " " << items[i].corner_x << " " << items[i].corner_y << " " << items[i].rotated << '\n';
    }
}

/*----------------- MAIN -----------------*/
signed main() {
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);
    freopen("INPUT.txt", "r", stdin);
    read_input();
    solve_problem();
    print_solution();
    return 0;
}
