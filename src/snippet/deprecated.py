import warnings
from functools import wraps


def deprecated(replacement=None):
    """
    A decorator which can be used to mark functions as deprecated.
    replacement is a callable that will be called with the same args
    as the decorated function.
    """
    def func_decorator(fun):
        msg = f"{fun.__name__} is deprecated"
        if replacement is not None:
            msg += f"; use {replacement.__name__} instead"
        if fun.__doc__ is None:
            fun.__doc__ = msg

        @wraps(fun)
        def actual_func(*args, **kwargs):
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return fun(*args, **kwargs)

        return actual_func
    return func_decorator


if __name__ == '__main__':
    warnings.filterwarnings("default", category=DeprecationWarning)

    def new_foo(x):
        return x + 1

    @deprecated(new_foo)
    def foo(x):
        return x
    ret = foo(1)
