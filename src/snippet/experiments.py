module_var = __name__ + ' var'


class Base:
    def __init__(self):
        super().__init__()
        print('in Base')


class A:
    def __init__(self):
        super().__init__()
        print('in A')


class B(Base):
    def __init__(self):
        super().__init__()
        print('in B')


class C(A):
    def __init__(self):
        super().__init__()
        print('in C')


class D(B, C):
    def __init__(self):
        super().__init__()
        print('in D')


class StaticMember:
    """try static attrs"""
    attr1: str = __doc__
    attr2: str = attr1 + '2'


if __name__ == '__main__':
    d = D()
    o = StaticMember()
    print(o.attr1, o.attr2)
    print(dir(StaticMember))
    print(StaticMember.__class__)
    main_mod = __import__(__name__)
    print(main_mod.module_var)
