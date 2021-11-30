from contextlib import contextmanager
from functools import wraps


def default_for_none_param(input_value):
    """
    one line statement to set default value for None
    >>> default_for_none_param(None)
    default value
    >>> default_for_none_param('my value')
    my value

    :param input_value: string
    :return: None
    """
    to_display = input_value or 'default value'
    print(to_display)


@contextmanager
def init_app():
    print('initializing ...')
    try:
        yield 1
    except:
        print('eat all exceptions')
    finally:
        print('clean up ...')


def mock_app():
    """
    >>> mock_app()
    initializing ...
    1
    eat all exceptions
    clean up ...

    :return:
    """
    with init_app() as context:
        print(str(context))
        raise Exception('Unhandled')


def suppress_exception_context():
    """
    >>> suppress_exception_context()
    ok

    :return:
    """
    from contextlib import suppress

    def _raise_exception():
        raise Exception('oops!')

    with suppress(Exception):
        _raise_exception()
    print('ok')


def positional_only_args(a, b, *, c='c'):
    """
    >>> positional_only_args('a', 'b')
    a b
    c
    >>> positional_only_args('a', b='b')
    a b
    c
    >>> positional_only_args('a', 'b', 'cc')
    Traceback (most recent call last):
    ...
    TypeError: positional_only_args() takes 2 positional arguments but 3 were given

    :param c:
    :param a:
    :param b:
    :param args:
    :return:
    """
    print(a, b)
    print(c)


def trace_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'executing {func.__name__}')
        func(*args, **kwargs)
    return wrapper


@trace_it
def being_traced(name: str):
    """
    >>> being_traced('ray')
    executing being_traced
    ray

    >>> being_traced.__wrapped__('ray')
    ray

    :param name:
    :return:
    """
    print(name)


class ReuseFunctionInClass:
    """
    >>> ReuseFunctionInClass.foo('aaa')
    aaa
    """
    from snippet.concise import one_liners as foo
    pass


class StaticPolymorphismBase:
    def run(self):
        print('Base instance method')


class StaticPolymorphism(StaticPolymorphismBase):
    """
    >>> a = StaticPolymorphism()
    >>> a.run()
    Derived static method
    """
    @staticmethod
    def run():
        print('Derived static method')


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
