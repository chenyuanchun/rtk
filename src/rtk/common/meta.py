from collections import namedtuple
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from time import strptime

__all__ = ['FieldType',
           'Field',
           'MetaMapper']


class FieldType(Enum):
    String = 1
    Integer = 2
    Float = 3
    Boolean = 4
    Decimal = 5
    Date = 6
    Timestamp = 7
    Json = 8

FieldDescription = namedtuple('FieldDescription', ('default', 'frompython', 'topython'))


def convert_to_python_date(value):
    if isinstance(value, str):
        try:
            value = date(*strptime(value, '%Y-%m-%d')[:3])
        except ValueError:
            raise ValueError('Invalid ISO date: {}'.format(value))
    return value


def convert_to_python_datetime(value):
    assert isinstance(value, str)
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as e:
        raise ValueError('Invalid ISO date/time %r' % value) from e


DEFAULT_CONVERTER = {
    FieldType.String: FieldDescription(None, str, str),
    FieldType.Integer: FieldDescription(0, lambda v: v, int),
    FieldType.Float: FieldDescription(0.0, str, float),
    FieldType.Boolean: FieldDescription(False, str, bool),
    FieldType.Decimal: FieldDescription(None, str, Decimal),
    FieldType.Date: FieldDescription(None,
                                     lambda v: v.isoformat() if isinstance(v, date) else v.date().isoformat(),
                                     convert_to_python_date),
    FieldType.Timestamp: FieldDescription(None,
                                          lambda v: v.isoformat()[:-3] + 'Z',
                                          convert_to_python_datetime)
}


class IConverter:
    """
    Interface of converter
    """
    def _to_python(self, value):
        """
        convert to python object
        :param value: dict
        :return: python object
        """

    def _from_python(self, value):
        """
        convert from python object
        :param value: python object
        :return: dict
        """


class Field(IConverter):
    """
    Field Descriptor of Python <-> SA Mapping
    """
    def __init__(self, name=None, type_=FieldType.String, description=None):
        self.name = name
        self.type = type_
        if self.type == FieldType.Json:
            raise NotImplementedError('Json field not implemented yet!')

        description = description if description else DEFAULT_CONVERTER[type_]
        self.default = description.default

        # use the field converter
        Field._from_python = description.frompython
        Field._to_python = description.topython
        # self.__from_python = description.frompython
        # self.__to_python = description.topython

    def __get__(self, instance, type_):
        if instance is None:  # operates at class level
            return self
        value = instance._data.get(self.name)
        if value is not None:
            value = self._to_python(value)
        elif self.default is not None:
            default = self.default
            value = default() if callable(default) else default
        return value

    def __set__(self, instance, value):
        if value is not None:
            value = self._from_python(value)
        instance._data[self.name] = value

    # def _to_python(self, value):
    #     return self.__to_python(value)
    #
    # def _from_python(self, value):
    #     return self.__from_python(value)


class MetaMapper(type):
    """
    Metaclass of all Python object <-> dict structure
    Create an internal class attribute _fields to hold all Field descriptions, including those from parents
    """
    def __new__(meta, name, bases, cls_dict):
        fields = {}
        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)
        for attr_name, attr_val in cls_dict.items():
            if isinstance(attr_val, Field):
                if not attr_val.name:
                    attr_val.name = attr_name
                fields[attr_name] = attr_val
        cls_dict['_fields'] = fields
        return super().__new__(meta, name, bases, cls_dict)
