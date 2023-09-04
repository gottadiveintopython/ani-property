import pytest


@pytest.fixture(scope='module', params=("AniNumericProperty", "AniSequenceProperty", ))
def descriptor_cls(request):
    import ani_property
    return getattr(ani_property, request.param)


@pytest.fixture()
def concrete_owner():
    from ani_property import AniNumericProperty, AniSequenceProperty
    class MyClass:
        ani_width = AniNumericProperty()
        ani_vector2d = AniSequenceProperty()
    return MyClass


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


def test_goal_value(concrete_owner):
    obj = concrete_owner()

    with pytest.raises(AttributeError):
        obj.ani_width
    with pytest.raises(AttributeError):
        obj.ani_vector2d

    obj.width = 0
    assert obj.ani_width == 0
    obj.vector2d = (0, 0)
    assert obj.ani_vector2d == (0, 0)

    obj.ani_width = 100
    assert obj.ani_width == 100
    assert obj.width == 0
    obj.ani_vector2d = (100, 100)
    assert obj.ani_vector2d == (100, 100)
    assert obj.vector2d == (0, 0)

    del obj._AniNumericProperty_actives['width']
    del obj._AniSequenceProperty_actives['vector2d']
    assert obj.ani_width == 0
    assert obj.ani_vector2d == (0, 0)
