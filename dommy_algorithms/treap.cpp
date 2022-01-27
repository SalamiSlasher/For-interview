#include <iostream>
#include <utility>
#include <random>

struct TreapNode {
    TreapNode *left = nullptr;
    TreapNode *right = nullptr;
    int underground;
    int value;
    int y;

    TreapNode() = default;

    TreapNode(int value, int y = rand(), int under = 1) : value(value), y(y), underground(under) {}
};


int Under(TreapNode *&T) {
    if (T == nullptr) {
        return 0;
    } else {
        return T->underground;
    }
}

void UpdateUnder(TreapNode *&T) {
    if (T != nullptr) {
        T->underground = Under(T->left) + Under(T->right) + 1;
    }
}

std::pair<TreapNode *, TreapNode *> Split(TreapNode *&T, int pos) {
    if (!T) {
        return std::make_pair(nullptr, nullptr);
    }
    auto cur = Under(T->left);
    if (cur < pos) {
        auto[l, r] = Split(T->right, pos - cur - 1);
        T->right = l;
        UpdateUnder(T);
        return std::make_pair(T, r);
    } else {
        auto[l, r] = Split(T->left,  pos);
        T->left = r;
        UpdateUnder(T);
        return std::make_pair(l, T);
    }
}

TreapNode *Merge(TreapNode *L, TreapNode *R) {
    if (L == nullptr) {
        return R;
    }
    if (R == nullptr) {
        return L;
    }
    if (L->y >= R->y) {
        L->right = Merge(L->right, R);
        UpdateUnder(L);
        return L;
    } else {
        R->left = Merge(L, R->left);
        UpdateUnder(R);
        return R;
    }
}

void Insert(TreapNode *&T, int pos, int value) {
    auto T_ = new TreapNode(value);
    auto[l, r] = Split(T, pos);
    T = Merge(Merge(l, T_), r);
}

void TaskA(TreapNode *T, int l, int r) {
    auto [L, R] = Split(T, r);
    auto [L_, M] = Split(L, l - 1);
    T = Merge(Merge(M, L_), R);
}

void Print(TreapNode *T) {
    if (!T) {
        return;
    }
    Print(T->left);
    std::cout << T->value << " ";
    Print(T->right);
}