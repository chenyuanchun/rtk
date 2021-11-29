from collections import namedtuple


Query = namedtuple('Query', 'y x')
Transition = namedtuple('Transition', 'y x state')

ALIVE = '*'
EMPTY = '-'


def count_neighbor(y, x):
    print('count_neighbor starts')
    n_ = yield Query(y+1, x)
    ne = yield Query(y+1, x+1)
    e_ = yield Query(y, x+1)
    se = yield Query(y-1, x+1)
    s_ = yield Query(y-1, x)
    sw = yield Query(y-1, x-1)
    w_ = yield Query(y, x-1)
    nw = yield Query(y+1, x-1)

    count = 0
    for state in (n_, ne, e_, se, s_, sw, w_, nw):
        if state == ALIVE:
            count += 1
    return count

if __name__ == '__main__':
    it = count_neighbor(10, 5)
    q1 = next(it)
    print('first: ', q1)
    q2 = it.send(ALIVE)
    print(q2)
    q3 = it.send(ALIVE)
    print(q3)
    q4 = it.send(ALIVE)
    print(q4)
    q5 = it.send(ALIVE)
    print(q5)
    q6 = it.send(ALIVE)
    print(q6)
    q7 = it.send(ALIVE)
    print(q7)
    q8 = it.send(ALIVE)
    print(q8)
    try:
        count = it.send(EMPTY)
    except StopIteration as e:
        print('count', e.value)


