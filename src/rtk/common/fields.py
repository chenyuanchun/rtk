import copy

from .meta import Field, FieldDescription
from .base import MapperBase


class ObjField(Field):
    """Field type for nested objects"""
    def __init__(self, mapping=None, name=None, default=None):
        default = default or {}
        super().__init__(name=name,
                         description=FieldDescription(lambda: default.copy(), str, str))
        self.mapping = mapping

    def _to_python(self, value):
        if self.mapping is None:
            return value
        else:
            return self.mapping.build_from(value)

    def _from_python(self, value):
        if self.mapping is None:
            return value
        if not isinstance(value, MapperBase):
            value = self.mapping(**value)
        return value.generate()


class TypedField(Field):
    """Experimental Field desc for enums"""
    def __init__(self, mappings, type_key='type', name=None, default=None):
        if default is not None:
            default = lambda: default.copy()
        super().__init__(name=name, description=FieldDescription(default, str, str))
        self.type_key = type_key
        self.mappings = mappings

    def _to_python(self, value):
        mapping = self.mappings[value[self.type_key]]
        return mapping.build_from(value)

    def _from_python(self, value):
        if isinstance(value, MapperBase):
            for value_type, mapping in self.mappings.iteritems():
                if isinstance(value, mapping):
                    break
            else:
                raise ValueError('Unknown value type')
        else:
            value_type = value[self.type_key]
            mapping = self.mappings[value_type]
            value = mapping(**value)
        value = value.generate()
        value[self.type_key] = value_type
        return value


class ListField(Field):
    """Field type for sequences"""
    def __init__(self, field, name=None, default=None):
        default = default or []
        super().__init__(name=name, description=FieldDescription(lambda: copy.copy(default),
                                                                 str, str))
        if type(field) is type:
            if issubclass(field, Field):
                field = field()
            elif issubclass(field, MapperBase):
                field = ObjField(field)
        self.field = field

    def _to_python(self, value):
        return self.Proxy(value, self.field)

    def _from_python(self, value):
        return [self.field._from_python(item) for item in value]

    class Proxy(list):
        def __init__(self, list_, field):
            self.list = list_
            self.field = field

        def __lt__(self, other):
            return self.list < other

        def __le__(self, other):
            return self.list <= other

        def __eq__(self, other):
            return self.list == other

        def __ne__(self, other):
            return self.list != other

        def __gt__(self, other):
            return self.list > other

        def __ge__(self, other):
            return self.list >= other

        def __repr__(self):
            return repr(self.list)

        def __str__(self):
            return str(self.list)

        def __unicode__(self):
            return str(self.list)

        def __delitem__(self, index):
            del self.list[index]

        def __getitem__(self, index):
            return self.field._to_python(self.list[index])

        def __setitem__(self, index, value):
            self.list[index] = self.field._from_python(value)

        def __delslice__(self, i, j):
            del self.list[i:j]

        def __getslice__(self, i, j):
            return ListField.Proxy(self.list[i:j], self.field)

        def __setslice__(self, i, j, seq):
            self.list[i:j] = (self.field._from_python(v) for v in seq)

        def __contains__(self, value):
            for item in self.list:
                if self.field._to_python(item) == value:
                    return True
            return False

        def __iter__(self):
            for index in range(len(self)):
                yield self[index]

        def __len__(self):
            return len(self.list)

        def __nonzero__(self):
            return bool(self.list)

        def append(self, *args, **kwargs):
            if args or not isinstance(self.field, ObjField):
                if len(args) != 1:
                    raise TypeError('append() takes exactly one argument '
                                    '({} given)'.format(len(args)))
                value = args[0]
            else:
                value = kwargs
            self.list.append(self.field._from_python(value))

        def count(self, value):
            return [i for i in self].count(value)

        def extend(self, list):
            for item in list:
                self.append(item)

        def index(self, value):
            return self.list.index(self.field._from_python(value))

        def insert(self, idx, *args, **kwargs):
            if args or not isinstance(self.field, ObjField):
                if len(args) != 1:
                    raise TypeError('insert() takes exactly 2 arguments '
                                    '({} given)'.format(len(args)))
                value = args[0]
            else:
                value = kwargs
            self.list.insert(idx, self.field._from_python(value))

        def remove(self, value):
            return self.list.remove(self.field._from_python(value))

        def pop(self, *args):
            return self.field._to_python(self.list.pop(*args))
