
def one_liners(param):
    b = param or 10
    print(str(b))


def try_catch(input_):
    try:
        _v = input_['key']
    except KeyError as e:
        raise Exception from e
    else:
        return _v


def step_generator(start=0, step=1, end=100):
    _start = start
    while _start < end:
        yield _start
        _start += step

if __name__ == '__main__':
    one_liners(0)
    one_liners(20)

    _gen = step_generator(1, 10)
    for idx in _gen:
        print(idx)
