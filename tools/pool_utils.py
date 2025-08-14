import platform
import multiprocessing as mp

from typing import Iterable

MAX_WIN32_WORKERS = 61


def __get_n_available_workers__():
    n_available_workers = mp.cpu_count()

    if platform.system() == "Windows":
        n_available_workers = MAX_WIN32_WORKERS if n_available_workers > MAX_WIN32_WORKERS else n_available_workers

    return n_available_workers


N_AVAILABLE_WORKERS = __get_n_available_workers__()


### Pooling for iterative task (output is a list)
def get_workers(n_workers=None):
    return n_workers if n_workers and n_workers < N_AVAILABLE_WORKERS else N_AVAILABLE_WORKERS


def pool_function(func, arg, n_workers=None):
    pool = mp.Pool(get_workers(n_workers))
    return pool.map(func, arg)


def starpool_function(func, args: Iterable[Iterable], n_workers=None):
    pool = mp.Pool(get_workers(n_workers))
    return pool.starmap(func, args)
