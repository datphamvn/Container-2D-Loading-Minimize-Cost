#include <bits/stdc++.h>
using namespace std;

const int MAX_N = 1000;
const int MAX_K = 1000;

// Dữ liệu đầu vào
int N, K;
int w[MAX_N], l[MAX_N]; // Kích thước của các item
int W[MAX_K], L[MAX_K], c[MAX_K]; // Kích thước và chi phí của các xe tải

// Biến lưu trữ kết quả
vector<int> result_t; // Xe tải mà item i được xếp vào
vector<int> result_x; // Tọa độ x của item i trong xe tải
vector<int> result_y; // Tọa độ y của item i trong xe tải
vector<int> result_o; // Trạng thái xoay của item i (0 hoặc 1)

// Biến ghi kết quả tốt nhất từng quan sát
vector<int> solution_t; // Xe tải mà item i được xếp vào
vector<int> solution_x; // Tọa độ x của item i trong xe tải
vector<int> solution_y; // Tọa độ y của item i trong xe tải
vector<int> solution_o; // Trạng thái xoay của item i (0 hoặc 1)

vector<int> used;

int min_cost = 1e6;

// Hàm kiểm tra xem item i có thể xếp vào xe tải thứ k không
bool canPlace(int i, int k, int x, int y, int o) {
    // Kiểm tra xem item có vượt quá kích thước của xe tải không
    if ((x + w[i]*(1-o) + l[i]*o) > W[k] || y + w[i]*o + l[i]*(1-o) > L[k]) {
        return false;
    }

    // Kiểm tra xem item có xếp chồng lên item khác không
    for (int j = 0; j < i; ++j) {
        if (result_t[j] == k &&
            !(x + w[i]*(1-o) + l[i]*o <= result_x[j] || result_x[j] + w[j]*(1-o) + l[j]*o <= x ||
              y + w[i]*o + l[i]*(1-o) <= result_y[j] || result_y[j] + w[j]*o + l[j]*(1-o) <= y)) {
            return false;
        }
    }
    return true;
}

int calcCost() {
    int totalCost = 0;
    for (int j = 0; j < K; ++j) {
        if (used[j] > 0)
            totalCost += c[j];
        }
    return totalCost;
}
// Hàm backtracking
void Try(int i) {
    if (i == N) {
        // Tính tổng chi phí sử dụng các xe tải
        int tmp = calcCost();

        // Kiểm tra chi phí có tốt không?
        if (tmp < min_cost){
            min_cost = tmp;
            for (int j = 0; j < N; ++j) {
                solution_t[j] = result_t[j];
                solution_x[j] = result_x[j];
                solution_y[j] = result_y[j];
                solution_o[j] = result_o[j];
            }
        }
        return;
    }

    for (int k = 0; k < K; ++k) {
        for (int x = 0; x <= W[k] - w[i]; x+=10) {
            for (int y = 0; y <= L[k] - l[i]; y+=10) {
                for (int o = 0; o < 2; ++o) {
                    if (canPlace(i, k, x, y, o)) {
                        used[k]++;
                        result_t[i] = k;
                        result_x[i] = x;
                        result_y[i] = y;
                        result_o[i] = o;
                        int tmp2 = calcCost();
                        if (tmp2 < min_cost) Try(i + 1);
                        used[k]--;
                    }
                }
            }
        }
    }
}

int main() {
    cin >> N >> K;
    for (int i = 0; i < N; ++i) {
        cin >> w[i] >> l[i];
    }
    for (int k = 0; k < K; ++k) {
        cin >> W[k] >> L[k] >> c[k];
    }

    result_t.resize(N, -1);
    result_x.resize(N);
    result_y.resize(N);
    result_o.resize(N);

    solution_t.resize(N, -1);
    solution_x.resize(N);
    solution_y.resize(N);
    solution_o.resize(N);

    used.resize(N, 0);
    Try(0);

    // In kết quả
    // cout << "min_cost: " << min_cost << endl;
    for (int j = 0; j < N; ++j) {
        cout << j + 1 << " " << solution_t[j] + 1 << " " << solution_x[j] << " "
            << solution_y[j] << " " << solution_o[j] << endl;
        }
    return 0;
}
