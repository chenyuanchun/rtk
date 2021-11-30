
def one_liners(param):
    """
    >>> one_liners(0)
    10
    >>> one_liners(9)
    9

    :param param:
    :return:
    """
    b = param or 10
    print(b)


def try_catch(input_):
    """
    :param input_:
    :return:

    >>> raise ValueError('value')
    Traceback (most recent call last):
      ...
    ValueError: value

    >>> try_catch({1:1})
    Traceback (most recent call last):
        ...
    KeyError: 'key'
    <BLANKLINE>
    The above exception was the direct cause of the following exception:
    <BLANKLINE>
    Traceback (most recent call last):
        ...
    Exception

    """
    try:
        _v = input_['key']
    except KeyError as e:
        raise Exception from e
    else:
        return _v


def step_generator(start=0, step=1, end=100):
    """
    Generator example to generate a range of numbers
    :param start:
    :param step:
    :param end:
    :return:
    >>> for idx in step_generator(1, 10, 30):
    ...   print(idx)
    1
    11
    21

    """
    _start = start
    while _start < end:
        yield _start
        _start += step

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
