from math import log

class SegmentTree:
    def left(self, vertex):
        return 2 * vertex + 1

    def right(self, vertex):
        return 2 * vertex + 2

    def parent(self, vertex):
        return (vertex - 1) // 2

    def __init__(self, arr, neutral=0):
        self.ROOT_INDEX = 0
        self.NEUTRAL_ELEMENT = neutral
        self.n = len(arr)
        if self.n < 2:
            self.arr = arr
            return

        self.arr = [self.NEUTRAL_ELEMENT] * (len(arr) - 1) + arr
        for i in range(self.n - 2, -1, -1):
            self.arr[i] = self.arr[self.left(i)] + self.arr[self.right(i)]

    def sum(self, l, r):
        return self.sum_h(self.ROOT_INDEX, 0, self.n - 1, l, r)

    def sum_h(self, v, vleft, vright, l, r):
        if l <= vleft and vright <= r:
            return self.arr[v]
        if vright < l or r < vleft:
            return self.NEUTRAL_ELEMENT
        vmed = (vleft + vright) // 2
        return (self.sum_h(self.left(v), vleft, vmed, l, r) +
                self.sum_h(self.right(v), vmed + 1, vright, l, r))

    def update(self, index, value):
        diff = -self.arr[index + self.n - 1] + value
        cur_index = index + self.n - 1
        while cur_index != self.ROOT_INDEX:
            self.arr[cur_index] += diff
            cur_index = self.parent(cur_index)
        self.arr[cur_index] += diff
