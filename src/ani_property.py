__all__ = (
    'AniNumericProperty', 'AniSequenceProperty',
    'add_property',
)

import typing as T
from functools import partial
import itertools
from kivy.metrics import dp
from kivy.clock import Clock


class AniNumericProperty:
    def __init__(self, *, threshold=dp(2), speed=10.0):
        self._threshold = threshold
        self._speed = speed

    def __set_name__(self, owner, name):
        if not name.startswith("ani_"):
            raise ValueError(f"The name of an {self.__class__.__name__} instance must start with 'ani_' (was {name!r}).")
        if len(name) < 5:
            raise ValueError(f"The name of an {self.__class__.__name__} instance must be no smaller than 5 (was {name!r}).")
        self._target_attr = name[4:]  # len('ani_') == 4

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
        actives[self._target_attr] = (goal_value, self._threshold, self._speed, )
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


class AniSequenceProperty:
    def __init__(self, *, threshold=dp(2), speed=10.0):
        self._threshold = threshold
        self._speed = speed

    def __set_name__(self, owner, name):
        if not name.startswith("ani_"):
            raise ValueError(f"The name of an {self.__class__.__name__} instance must start with 'ani_' (was {name!r}).")
        if len(name) < 5:
            raise ValueError(f"The name of an {self.__class__.__name__} instance must be no smaller than 5 (was {name!r}).")
        self._target_attr = name[4:]  # len('ani_') == 4

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
        actives[self._target_attr] = (goal_seq, getattr(obj, self._target_attr), self._threshold, self._speed, )
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
                # This is a Kivy specific thing. If the 'obj' is an EventDispatcher and the 'target_attr' is the name
                # of a Kivy property, this will notify the 'obj' that the content of the sequence has changed.
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
