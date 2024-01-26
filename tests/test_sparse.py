import numpy as np
from numpy.testing import assert_equal
import pytest
import sparse

import finch


@pytest.fixture
def x():
    return finch.fsprand(5, 5, 0.5)


@pytest.fixture
def y():
    return finch.fsprand(5, 5, 0.5)


@pytest.fixture
def arr3d():
    return np.array(
        [
            [[0, 1, 0, 0], [1, 0, 0, 3]],
            [[4, 0, -1, 0], [2, 2, 0, 0]],
            [[0, 0, 0, 0], [1, 5, 0, 3]],
        ]
    )


@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.mark.parametrize("dtype", [np.int64, np.float64, np.complex128])
def test_wrappers(dtype):
    A = np.array([[0, 0, 4], [1, 0, 0], [2, 0, 5], [3, 0, 0]], dtype=dtype)
    B = np.stack([A, A], axis=2, dtype=dtype)
    scalar = finch.Tensor(finch.Element(2), np.array(2))

    levels = finch.Dense(finch.SparseList(finch.SparseList(finch.Element(dtype(0.0)))))
    B_finch = finch.Tensor(levels, B)

    assert_equal(B_finch.todense(), B)
    assert_equal((B_finch * scalar + B_finch).todense(), B * 2 + B)

    levels = finch.Dense(finch.Dense(finch.Element(dtype(1.0))))
    A_finch = finch.Tensor(levels, A)

    assert_equal(A_finch.todense(), A)
    assert_equal((A_finch * scalar + A_finch).todense(), A * 2 + A)

    assert A_finch.todense().dtype == A.dtype and B_finch.todense().dtype == B.dtype
    assert not A_finch.todense().flags.f_contiguous


def test_coo(rng):
    coords = np.asarray(
        [[0, 1, 2, 3, 4], [0, 1, 2, 3, 4]],
        dtype=np.intp,
    )
    data = rng.random(5)
    scalar = finch.Tensor(finch.Element(2), np.array(2))

    arr_pydata = sparse.COO(coords, data, shape=(5, 5))
    arr = arr_pydata.todense()
    arr_finch = finch.COO(coords, data, shape=(5, 5))

    assert_equal(arr_finch.todense(), arr)
    assert_equal((arr_finch * scalar + arr_finch).todense(), arr * 2 + arr)

    assert arr_finch.todense().dtype == data.dtype
    assert not arr_finch.todense().flags.f_contiguous


@pytest.mark.parametrize(
    "classes",
    [(sparse._compressed.CSC, finch.CSC), (sparse._compressed.CSR, finch.CSR)],
)
def test_compressed2d(rng, classes):
    sparse_class, finch_class = classes
    indices, indptr, data = np.arange(5), np.arange(6), rng.random(5)
    scalar = finch.Tensor(finch.Element(2), np.array(2))

    arr_pydata = sparse_class((data, indices, indptr), shape=(5, 5))
    arr = arr_pydata.todense()
    arr_finch = finch_class((data, indices, indptr), shape=(5, 5))

    assert_equal(arr_finch.todense(), arr)
    assert_equal((arr_finch * scalar + arr_finch).todense(), arr * 2 + arr)

    assert arr_finch.todense().dtype == data.dtype
    assert not arr_finch.todense().flags.f_contiguous


def test_csf(arr3d):
    arr = arr3d
    scalar = finch.Tensor(finch.Element(2), np.array(2))

    data = np.array([4, 1, 2, 1, 1, 2, 5, -1, 3, 3])
    indices_list = [
        np.array([1, 0, 1, 2, 0, 1, 2, 1, 0, 2]),
        np.array([0, 1, 0, 1, 0, 1]),
    ]
    indptr_list = [np.array([0, 1, 4, 5, 7, 8, 10]), np.array([0, 2, 4, 5, 6])]

    arr_finch = finch.CSF((data, indices_list, indptr_list), shape=(3, 2, 4))

    assert_equal(arr_finch.todense(), arr)
    assert_equal((arr_finch * scalar + arr_finch).todense(), arr * 2 + arr)

    assert arr_finch.todense().dtype == data.dtype
    assert not arr_finch.todense().flags.f_contiguous


@pytest.mark.parametrize(
    "permutation", [(0, 1, 2), (2, 1, 0), (0, 2, 1), (1, 2, 0)]
)
def test_permute_dims(arr3d, permutation):
    arr = arr3d

    levels = finch.Dense(finch.SparseList(finch.SparseList(finch.Element(0))))
    arr_finch = finch.Tensor(levels, arr)

    actual = finch.permute_dims(arr_finch, permutation)
    expected = np.transpose(arr, permutation)

    assert actual._is_swizzle()
    assert_equal(actual.todense(), expected)

    actual = finch.permute_dims(actual, permutation)
    expected = np.transpose(arr, permutation)

    assert actual._is_swizzle()
    assert_equal(actual.todense(), expected)

    assert not (actual + arr_finch)._is_swizzle()
