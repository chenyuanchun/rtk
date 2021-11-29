class ConvertToDict:
    def to_dict(self):
        return self._traverse(self.__dict__)

    @staticmethod
    def _traverse(value):
        if isinstance(value, ConvertToDict):
            return value.to_dict()
        elif isinstance(value, dict):
            return {key: ConvertToDict._traverse(_value) for key, _value in value.items()}
        elif isinstance(value, (list, tuple)):
            return [ConvertToDict._traverse(i) for i in value]
        elif hasattr(value, '__dict__'):
            return {key: ConvertToDict._traverse(_value) for key, _value in value.__dict__.items()}
        else:
            return value


