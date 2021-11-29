from pprint import pprint
from rtk.common.mixin import ConvertToDict


class SimpleObject:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 'blah'
        self.list_attr = [10, 20, 30]
        self.tuple_attr = (4, 5, 6)
        self.dict_attr = {
            100: 'google',
            102: 'ms'
        }


class ComplexObject(ConvertToDict):
    def __init__(self):
        self.dict_data = {
            1: 'aa',
            2: 'bb'
        }
        self.list_data = [1, 3, 5]
        self.dict_of_dict = {
            3: {
                4: 'cc',
                5: 'dd'
            },
            4: 100
        }


class MoreComplex(ConvertToDict):
    def __init__(self):
        self.simple = SimpleObject()
        self.complex = ComplexObject()
        self.dict_data = {
            5: 105,
            6: 'ee'
        }
        self.list_complex = [ComplexObject(), ComplexObject()]


def test_convert_class_to_dict():
    _obj = MoreComplex()
    pprint(_obj.to_dict())
