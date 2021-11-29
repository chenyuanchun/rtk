from pprint import pprint

from rtk.common.utils import traverse_complex_data, traverse_process_complex_data


def test_traverse():
    data = {
        1: 'aa',
        2: 'bb',
        3: [2, 4, 6],
        4: {
            'a': 'bb',
            'b': 'cc'
        }
    }

    traverse_complex_data(data, print)


def test_traverse_replace():
    data = {
        1: 'aa',
        2: 'bb',
        3: ['dd', 'ee', 'ff'],
        4: {
            'a': 'bb',
            'b': 'cc'
        }
    }

    ret = traverse_process_complex_data(data, str.upper)
    pprint(ret)
