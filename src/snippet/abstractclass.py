import abc


class AbstractBase(abc.ABC):
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def foo(self, input_value):
        """This is an abstract method"""


class Concrete(AbstractBase):
    def foo(self, input_value):
        pass


@AbstractBase.register
class Other:
    """
    Example of `abc.register`
    >>> o = Other()
    >>> isinstance(o, AbstractBase)
    True
    """
    pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
