#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <vector>

template <typename T>
class Matrix {
    std::vector<T> data_;
    size_t rows_ = 0;
    size_t cols_ = 0;

public:
    Matrix(const std::vector<std::vector<T>>& m) : rows_(m.size()) {
        if (m.empty()) {
            return;
        }
        cols_ = m[0].size();
        data_.resize(cols_ * rows_);

        for (size_t i = 0; i < rows_; ++i) {
            std::copy(m[i].begin(), m[i].end(), data_.data() + i * cols_);
        }
    }

    Matrix& operator += (const Matrix& B) {
        assert(rows_ == B.rows_ && cols_ == B.cols_);
        for (size_t i = 0; i < rows_ * cols_; ++i) {
            data_[i] += B.data_[i];
        }
        return *this;
    }

    Matrix operator + (const Matrix& B) const {
        assert(rows_ == B.rows_ && cols_ == B.cols_);
        Matrix result = *this;
        result += B;
        return result;
    }
    Matrix& operator *= (const Matrix& other) {
        assert(cols_ == other.rows_);
        std::vector<T> data_new(rows_ * other.cols_);

        for (size_t i = 0; i < rows_ ; ++i) {
            for (size_t j = 0; j < other.cols_; ++j) {
                for (size_t k = 0; k < other.rows_; ++k) {
                    data_new[i * other.cols_ + j] += data_[i * cols_ + k]
                            * other.data_[k * other.cols_ + j];
                }
            }
        }
        cols_ = other.cols_;
        data_ = data_new;
        return *this;
    }

    Matrix operator * (const Matrix& other) const {
        assert(cols_ == other.rows_);
        Matrix result = *this;
        result *= other;
        return result;
    }

    auto begin() {
        return data_.begin();
    }
    auto begin() const {
        return data_.begin();
    }
    auto end() {
        return data_.end();
    }
    auto end() const {
        return data_.end();
    }

    template <typename U>
    Matrix& operator *= (const U& lambda) {
        for (size_t i = 0; i < rows_ * cols_; ++i) {
            data_[i] *= lambda;
        }
        return *this;
    }

    template <typename U>
    Matrix operator * (const U& lambda) const {
        Matrix result = *this;
        result *= lambda;
        return result;
    }

    Matrix& transpose() {
        std::vector<T> data_copy(data_.size());
        std::copy(data_.begin(), data_.end(), data_copy.begin());

        for (size_t i = 0; i < cols_; ++i) {
            for (size_t j = 0; j < rows_ ; ++j) {
                data_[j + rows_ * i] = data_copy[j * cols_ + i];
            }
        }
        std::swap(rows_, cols_);
        return *this;
    }

    Matrix transposed() const {
        Matrix result = *this;
        result.transpose();
        return result;
    }

    T* operator[] (size_t index) {
        return data_.data() + index * cols_;
    }

    const T* operator[] (size_t index) const {
        return data_.data() + index * cols_;
    }

    std::pair<size_t, size_t> size() const {
        return {rows_, cols_};
    }
};

template <typename T>
std::ostream& operator<<(std::ostream& out, const Matrix<T>& m) {
    auto [rows, cols] = m.size();
    for (size_t i = 0; i < rows; ++i) {
        std::copy(m[i], m[i] + cols - 1, std::ostream_iterator<T>(out, "\t"));
        out << m[i][cols - 1];
        if (i + 1 != rows) {
            out << "\n";
        }
    }
    return out;
}
