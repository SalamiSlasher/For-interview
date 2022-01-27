#include <algorithm>
#include <iostream>
#include <vector>
#include <tuple>

class DisjointSet {
    std::vector<size_t> disjoint_set;
    std::vector<size_t> rank;
    std::vector<size_t> cash;
    size_t n;

public:
    DisjointSet(size_t n) : n(n), rank(n + 1, 1) {
        for (size_t i = 0; i < n + 1; ++i) {
            disjoint_set.push_back(i);
        }
    }

    size_t Find(size_t x) {
        cash.clear();
        cash.push_back(x);

        while (x != disjoint_set[x]) {
            x = disjoint_set[x];
            cash.push_back(x);
        }

        for (auto v : cash) {
            disjoint_set[v] = x;
        }
        return x;
    }

    void Union(size_t x, size_t y) {
        if (Find(x) > Find(y)) {
            std::swap(x, y);
        }
        rank[Find(y)] += rank[Find(x)];
        disjoint_set[Find(x)] = Find(y);
    }

    void Print() const {
        for (int i = 1; i < n + 1; ++i) {
            std::cout << i << ": " << disjoint_set[i] << " \n";
        }
    }
};
