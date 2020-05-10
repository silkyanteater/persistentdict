import os
import pytest

from persistentdict import PersistentDict


@pytest.fixture
def pd():
    return PersistentDict(":memory:")


def test_simple_values(pd):
    assert len(pd) == 0
    pd['x'] = 42
    assert pd['x'] == 42
    assert len(pd) == 1
    pd['y'] = 42.42
    assert pd['y'] == 42.42
    assert len(pd) == 2
    pd['z'] = 'string'
    assert pd['z'] == 'string'
    assert len(pd) == 3

def test_structures(pd):
    assert len(pd) == 0
    pd['x'] = ()
    assert pd['x'] == ()
    assert len(pd) == 1
    pd['y'] = ['y']
    assert pd['y'] == ['y']
    assert len(pd) == 2
    pd['z'] = {'key': 'value'}
    assert pd['z'] == {'key': 'value'}
    assert len(pd) == 3
    pd.clear()
    assert len(pd) == 0

def test_methods(pd):
    counterdict = {'x': 42, 'y': 42.42, 'z': 'string'}
    for key, value in counterdict.items():
        pd[key] = value
    assert pd.copy() == counterdict
    for key in pd:
        assert key in counterdict
    for key in pd.keys():
        assert key in counterdict
    for value in pd.values():
        assert value in set(counterdict.values())
    for key, value in pd.items():
        assert counterdict[key] == value
    pd.replace(counterdict)
    assert pd.copy() == counterdict
    extradict = {'a': 8, 'b': 'nine'}
    pd.update(extradict)
    counterdict.update(extradict)
    assert pd.copy() == counterdict
    assert pd.pop('a') == counterdict.pop('a')
    with pytest.raises(KeyError):
        pd.pop('q')
    assert pd.pop('q', 139) == 139
    assert pd.setdefault('x', 31) == 42
    assert pd.setdefault('u', 31) == 31
    counterdict.setdefault('u', 31)
    assert pd.copy() == counterdict
    for _ in range(len(pd)):
        item = pd.popitem()
        assert counterdict[item[0]] == item[1]
    with pytest.raises(KeyError):
        pd.popitem()
