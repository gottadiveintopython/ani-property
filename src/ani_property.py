__all__ = (
    'AniNumericProperty', 'AniMutableSequenceProperty', 'AniSequenceProperty',
    'add_property', 'install',
)

import typing as T
from functools import partial
import itertools
from kivy.metrics import dp
from kivy.clock import Clock


class AniNumericProperty:
    '''
    Descriptor that animates an attribute that holds a numeric value.
    '''
    def __init__(self, *, threshold=dp(2), speed=10.0):
        self.threshold = threshold
        self.speed = speed

    def __set_name__(self, owner, name):
        if name.startswith("ani_") and len(name) > 4:  # len('ani_') == 4
            self._target_attr = name[4:]
        elif name.startswith("_ani_") and len(name) > 5:  # len('_ani_') == 5
            self._target_attr = name[5:]
        else:
            raise ValueError(
                f"The name of an {self.__class__.__name__} instance must start with either 'ani_' or '_ani_', "
                f"and at least one character must follow it (was {name!r})."
            )

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj._AniNumericProperty_actives[self._target_attr][0]
        except (AttributeError, KeyError):
            return getattr(obj, self._target_attr)

    def __set__(self, obj, goal_value):
        try:
            actives = obj._AniNumericProperty_actives
            trigger = obj._AniNumericProperty_trigger
        except AttributeError:
            actives = {}
            trigger = Clock.create_trigger(partial(self._animate, obj, actives), 0, True)
            obj._AniNumericProperty_actives = actives
            obj._AniNumericProperty_trigger = trigger
        actives[self._target_attr] = (goal_value, self.threshold, self.speed, )
        trigger()

    def _animate(abs, setattr, getattr, obj, actives, dt):
        for target_attr, (goal_value, threshold, speed) in actives.copy().items():
            cur_value = getattr(obj, target_attr)
            diff = goal_value - cur_value
            if abs(diff) > threshold and (p := dt * speed) < 1.0:
                new_value = diff * p + cur_value
            else:
                new_value = goal_value
                del actives[target_attr]
            setattr(obj, target_attr, new_value)
        
        # Stop the ClockEvent instance if there is nothing left to animate
        if not actives:
            return False

    _animate = staticmethod(partial(_animate, abs, setattr, getattr))

    def cancel(self, obj):
        try:
            del obj._AniNumericProperty_actives[self._target_attr]
        except (AttributeError, KeyError):
            pass


class AniMutableSequenceProperty:
    '''
    Descriptor that animates an attribute that holds a mutable sequence of numbers.

    .. code-block::

        class MyClass:
            ani_color = AniMutableSequenceProperty(threshold=1.0)

        obj = MyClass()
        obj.color = [255, 255, 255, 255]
        obj.ani_color = [255, 0, 0, 255]

    The ``obj.color`` will be updated in-place, which means the ``obj`` won't notice it because ``obj.__setattr__()``
    won't be called. If the sequence is a custom object that has a ``__setitem__()`` method, it would notice the
    update, and is able to tell it anyone else. But in case it's not, like the above example,
    ``AniMutableSequenceProperty`` re-assigns the sequence to the attribute so that the ``obj`` can notice the update.
    '''
    def __init__(self, *, threshold=dp(2), speed=10.0):
        self.threshold = threshold
        self.speed = speed

    def __set_name__(self, owner, name):
        if name.startswith("ani_") and len(name) > 4:  # len('ani_') == 4
            self._target_attr = name[4:]
        elif name.startswith("_ani_") and len(name) > 5:  # len('_ani_') == 5
            self._target_attr = name[5:]
        else:
            raise ValueError(
                f"The name of an {self.__class__.__name__} instance must start with either 'ani_' or '_ani_', "
                f"and at least one character must follow it (was {name!r})."
            )

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj._AniMutableSequenceProperty_actives[self._target_attr][0]
        except (AttributeError, KeyError):
            return getattr(obj, self._target_attr)

    def __set__(self, obj, goal_seq):
        try:
            actives = obj._AniMutableSequenceProperty_actives
            trigger = obj._AniMutableSequenceProperty_trigger
        except AttributeError:
            actives = {}
            trigger = Clock.create_trigger(partial(self._animate, obj, actives), 0, True)
            obj._AniMutableSequenceProperty_actives = actives
            obj._AniMutableSequenceProperty_trigger = trigger
        actives[self._target_attr] = (goal_seq, getattr(obj, self._target_attr), self.threshold, self.speed, )
        trigger()

    def _animate(itertools_count, zip, abs, setattr, obj, actives, dt):
        for target_attr, (goal_seq, cur_seq, threshold, speed) in actives.copy().items():
            any_updates = False
            for cur_elem, goal_elem, idx in zip(cur_seq, goal_seq, itertools_count()):
                diff = goal_elem - cur_elem
                if not diff:
                    continue
                any_updates = True
                if abs(diff) > threshold and (p := dt * speed) < 1.0:
                    cur_seq[idx] = diff * p + cur_elem
                else:
                    cur_seq[idx] = goal_elem
            if any_updates:
                # The re-assignment mentioned in the class doc. 
                setattr(obj, target_attr, cur_seq)
            else:
                del actives[target_attr]
        
        # Stop the ClockEvent instance if there is nothing left to animate
        if not actives:
            return False

    _animate = staticmethod(partial(_animate, itertools.count, zip, abs, setattr))

    def cancel(self, obj):
        try:
            del obj._AniMutableSequenceProperty_actives[self._target_attr]
        except (AttributeError, KeyError):
            pass


class AniSequenceProperty:
    '''
    Descriptor that animates an attribute that holds a mutable/immutable sequence of numbers.

    Unlike :class:`AniMutableSequenceProperty`, this one creates a new sequence and assigns it to the attribute on every
    update.
    '''
    def __init__(self, *, threshold=dp(2), speed=10.0, sequence_cls=tuple):
        self.threshold = threshold
        self.speed = speed
        self.sequence_cls = sequence_cls

    def __set_name__(self, owner, name):
        if name.startswith("ani_") and len(name) > 4:  # len('ani_') == 4
            self._target_attr = name[4:]
        elif name.startswith("_ani_") and len(name) > 5:  # len('_ani_') == 5
            self._target_attr = name[5:]
        else:
            raise ValueError(
                f"The name of an {self.__class__.__name__} instance must start with either 'ani_' or '_ani_', "
                f"and at least one character must follow it (was {name!r})."
            )

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj._AniSequenceProperty_actives[self._target_attr][0]
        except (AttributeError, KeyError):
            return getattr(obj, self._target_attr)

    def __set__(self, obj, goal_seq):
        try:
            actives = obj._AniSequenceProperty_actives
            trigger = obj._AniSequenceProperty_trigger
        except AttributeError:
            actives = {}
            trigger = Clock.create_trigger(partial(self._animate, obj, actives), 0, True)
            obj._AniSequenceProperty_actives = actives
            obj._AniSequenceProperty_trigger = trigger
        actives[self._target_attr] = (
            goal_seq, self.threshold, self.speed, self.sequence_cls,
        )
        trigger()

    def _animate(bool, zip, abs, setattr, getattr, obj, actives, dt):
        for target_attr, (goal_seq, threshold, speed, sequence_cls) in actives.copy().items():
            cur_seq = getattr(obj, target_attr)
            any_updates = False
            new_sequence = sequence_cls(
                (diff * p + cur_elem)
                if (diff := goal_elem - cur_elem, any_updates := (any_updates or bool(diff)), ) \
                    and abs(diff) > threshold and (p := dt * speed) < 1.0
                else goal_elem
                for cur_elem, goal_elem in zip(cur_seq, goal_seq)
            )
            if any_updates:
                setattr(obj, target_attr, new_sequence)
            else:
                del actives[target_attr]
        
        # Stop the ClockEvent instance if there is nothing left to animate
        if not actives:
            return False

    _animate = staticmethod(partial(_animate, bool, zip, abs, setattr, getattr))

    def cancel(self, obj):
        try:
            del obj._AniSequenceProperty_actives[self._target_attr]
        except (AttributeError, KeyError):
            pass


def add_property(cls, name, descriptor):
    setattr(cls, name, descriptor)
    descriptor.__set_name__(cls, name)


def install(*, target=None, prefix:T.Literal['ani_', '_ani_']='ani_'):
    '''
    Adds the ``ani_xxx`` version of sizing/positioning properties (excluding ``pos_hint``) to the
    :class:`kivy.uix.widget.Widget`.

    .. code-block::

        from kivy.uix.widget import Widget
        import ani_property

        ani_property.install()

        widget = Widget()
        widget.ani_x = 300
        widget.ani_size_hint_x = 2.0

    If you don't want to pollute the ``Widget``, specify your own widget class through the ``target`` parameter.

    .. code-block::

        install(target=YourOwnWidgetClass)
    '''

    # LOAD_FAST
    _hasattr = hasattr
    _add_property = add_property
    _AniNumericProperty = AniNumericProperty
    _AniMutableSequenceProperty = AniMutableSequenceProperty

    if target is None:
        from kivy.uix.widget import Widget as target

    numeric_property_names = (
        'opacity',
        'x', 'y', 'center_x', 'center_y', 'right', 'top', 'width', 'height',
        'size_hint_x', 'size_hint_y', 'size_hint_min_x', 'size_hint_min_y', 'size_hint_max_x', 'size_hint_max_y',
    )
    for name in numeric_property_names:
        assert _hasattr(target, name)
        _add_property(target, prefix + name, _AniNumericProperty())

    sequence_property_names = (
        'pos', 'center', 'size', 'size_hint', 'size_hint_min', 'size_hint_max',
    )
    for name in sequence_property_names:
        assert _hasattr(target, name)
        _add_property(target, prefix + name, _AniMutableSequenceProperty())
