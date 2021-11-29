from rtk.common.expression import Expression


def test_happy_path():
    exp = Expression('${aa} if ${aa} == ${bb} else ${bb}')
    ret = exp(aa='a', bb='b')
    assert ret == 'b'
    assert exp(aa='a', bb='a') == 'a'


def mock_func(*args):
    return args[0]*10


def test_invoke_function():
    _exp = Expression('run_func(${aa})')
    ret = _exp({'run_func': mock_func}, aa='a')
    assert ret == 'a'*10
