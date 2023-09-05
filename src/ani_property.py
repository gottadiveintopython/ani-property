__all__ = (
    'AniNumericProperty', 'AniMutableSequenceProperty',
    'add_property',
)

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


class AniMutableSequenceProperty:
    '''
    Descriptor that animates an attribute that holds a mutable sequence of numbers.

    .. code-block::

        class MyClass:
            ani_color = AniMutableSequenceProperty(threshold=1.0)

        obj = MyClass()
        obj.color = [255, 255, 255, 255]
        obj.ani_color = [255, 0, 0, 255]

    The 'obj.color' will be updated in-place, which means the 'obj' won't notice it because 'obj.__setattr__()' won't
    be called. If the sequence is a custom object that has a '__setitem__()' method, it will notice the update, and
    is able to tell it anyone else. But in case it's not, like the above example, ``AniMutableSequenceProperty``
    re-assigns the sequence to the attribute so that the 'obj' can notice the update.
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


def add_property(cls, name, descriptor):
    setattr(cls, name, descriptor)
    descriptor.__set_name__(cls, name)
