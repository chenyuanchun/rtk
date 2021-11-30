from .meta import MetaMapper, IConverter


class MapperBase(IConverter, metaclass=MetaMapper):

    def __init__(self, **values):
        self._data = {}
        for attr_name, field in self._fields.items():
            if attr_name in values:
                setattr(self, attr_name, values.pop(attr_name))
            else:
                setattr(self, attr_name, getattr(self, attr_name))

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self._data)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data or ())

    def __delitem__(self, name):
        del self._data[name]

    def __getitem__(self, name):
        return self._data[name]

    def __setitem__(self, name, value):
        self._data[name] = value

    def get(self, name, default=None):
        return self._data.get(name, default)

    def setdefault(self, name, default):
        return self._data.setdefault(name, default)

    def generate(self):
        return self._data

    @classmethod
    def create_type_from(cls, **d):
        fields = {}
        for attr_name, attr_val in d.items():
            if not attr_val.name:
                attr_val.name = attr_name
            fields[attr_name] = attr_val
        d['_fields'] = fields
        return type('AnonymousSAType', (cls,), d)

    @classmethod
    def build_from(cls, data):
        instance = cls()
        instance._data = data
        return instance

    def _to_python(self, value):
        return self.build_from(value)

    def _from_python(self, value):
        return self.generate()

    def items(self):
        return self._data.items()

