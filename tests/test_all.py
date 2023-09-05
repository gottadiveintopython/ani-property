import pytest


descriptor_cls_names = (
    "AniNumericProperty", "AniMutableSequenceProperty", "AniSequenceProperty",
)


@pytest.fixture(scope='module', params=descriptor_cls_names)
def descriptor_cls(request):
    import ani_property
    return getattr(ani_property, request.param)


@pytest.mark.parametrize('name', ("x", "_ani_", "ani_", "hello_everyone"))
def test_invalid_name(name, descriptor_cls):
    with pytest.raises(RuntimeError) as excinfo:
        type('MyClass', tuple(), {name: descriptor_cls(), })
    assert isinstance(excinfo.value.__cause__, ValueError)


@pytest.mark.parametrize('name', ("x", "_ani_", "ani_", "hello_everyone"))
def test_invalid_name_ver_dynamic(name, descriptor_cls):
    from ani_property import add_property
    MyClass = type('MyClass', tuple(), {})
    with pytest.raises(ValueError):
        add_property(MyClass, name, descriptor_cls())


def test_get_descriptor(descriptor_cls):
    MyClass = type('MyClass', tuple(), {'ani_attr': descriptor_cls(), })
    assert MyClass.ani_attr.__class__ is descriptor_cls


def test_get_descriptor_ver_dynamic(descriptor_cls):
    from ani_property import add_property
    MyClass = type('MyClass', tuple(), {})
    add_property(MyClass, 'ani_attr', descriptor_cls())
    assert MyClass.ani_attr.__class__ is descriptor_cls


@pytest.mark.parametrize(
    "descriptor_cls_name, value1, value2", [
        ["AniNumericProperty", 0, 100],
        ["AniMutableSequenceProperty", [10, 20, ], [30, 40, ]],
        ["AniSequenceProperty", (10, 20, ), (30, 40, )],
    ]
)
def test_goal_value(descriptor_cls_name, value1, value2):
    import ani_property

    descriptor_cls = getattr(ani_property, descriptor_cls_name)
    MyClass = type('MyClass', tuple(), {'ani_attr': descriptor_cls(), })
    obj = MyClass()

    with pytest.raises(AttributeError):
        obj.ani_attr
    obj.attr = value1
    assert obj.ani_attr == value1
    obj.ani_attr = value2
    assert obj.ani_attr == value2
    assert obj.attr == value1
    del getattr(obj, f"_{descriptor_cls_name}_actives")['attr']
    assert obj.ani_attr == value1
    assert obj.attr == value1


@pytest.mark.parametrize(
    "goal_seq, cur_seq, expected_seq", [
        [(0, 1, ), (0, 1, ), (0, 1, ), ],
        [(4, 4, ), (0, 1, ), (0, 1, ), ],
        [(0, 1, ), (4, 4, ), (0, 1, ), ],
        [(3, 1, ), (2, 4, ), (2, 1, ), ],
        [(1, 3, ), (4, 2, ), (1, 2, ), ],
        [(2, 1, ), (2, 4, ), (2, 1, ), ],
        [(1, 2, ), (4, 2, ), (1, 2, ), ],
    ]
)
def test_complicated_generator_comprehension(goal_seq, cur_seq, expected_seq):
    any_updates = False
    new_seq = tuple(
        cur_elem
        if (diff := goal_elem - cur_elem, any_updates := (any_updates or (diff < 0)), ) and goal_elem > cur_elem 
        else goal_elem
        for cur_elem, goal_elem in zip(cur_seq, goal_seq)
    )
    assert new_seq == expected_seq
    assert any_updates is (cur_seq != new_seq)
