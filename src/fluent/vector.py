from math import hypot


class Vector:
    def __init__(self, x=0, y=0):
        """
        >>> Vector(2, 4)
        Vector(2,4)
        """
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector({self.x},{self.y})'

    def __abs__(self):
        """
        >>> a = Vector(2, 4)
        >>> abs(a)
        4.47213595499958

        :return:
        """
        return hypot(self.x, self.y)

    def __bool__(self):
        """
        >>> a = Vector(2, 4)
        >>> bool(a)
        True
        >>> bool(Vector(0, 0))
        False

        :return:
        """
        return bool(abs(self))

    def __add__(self, other):
        """
        >>> Vector(1,2) + Vector(2,3)
        Vector(3,5)

        :param other:
        :return:
        """
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        """
        >>> Vector(1,2) * 2
        Vector(2,4)

        :param other:
        :return:
        """
        return Vector(self.x * other, self.y * other)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
