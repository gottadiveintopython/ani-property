# AniProperty

A set of Python descriptors that animate numeric attributes of any object in a Kivy application.

[Youtube](https://youtu.be/AI8YF3LvNqU)

```python
from kivy.uix.wiget import Widget
from ani_property import AniNumericProperty


class CustomWidget(Widget):
    ani_x = AniNumericProperty()
    ani_y = AniNumericProperty()


widget = CustomWidget(x=0, y=50)
widget.ani_x = 100  # -> animates 'widget.x' from 0 to 100
widget.ani_y = 200  # -> animates 'widget.y' from 50 to 200
```

The application of the descriptors is not limited to Kivy properties.
As long as Kivy is running, it can animate any types of numeric attribute.

```python
from ani_property import AniNumericProperty


class MyClass:
    ani_value = AniNumericProperty()


obj = MyClass()
obj.value = 40
obj.ani_value = 100  # -> animates 'obj.value' from 40 to 100
```

You can cancel the animation as follows.

```python
MyClass.ani_value.cancel(obj)
```

You can also add a descriptor to a class outside of its definition. 

```python
from ani_property import AniNumericProperty, add_property

add_property(CustomWidget, 'ani_width', AniNumericProperty())
```

## Sequence-type Attribute

You can animate a number sequence as well.

```python
from kivy.uix.label import Label
from ani_property import AniMutableSequenceProperty


# WARNING: Changing the 'Label.color' causes the 'Label' to re-create its texture
# so animating it may be expensive.
class CustomLabel(Label):
    ani_color = AniMutableSequenceProperty(threshold=0.02)


label = CustomLabel(color=(1.0, 1.0, 1.0, 1.0))
label.ani_color = (1.0, 0.0, 0.0, 1.0)  # animates 'label.color' from white to red
```

There are two types of descriptors for sequence-type attributes.

- `AniMutableSequenceProperty` modifies the sequence in-place.
- `AniSequenceProperty` creates a new sequence and assigns it to the target attribute

## Performance Tip

It may be better to use `AniNumericProperty` instead of `AniMutableSequenceProperty` or `AniSequenceProperty` when
your app animates a lot of stuffs at a time.

```python
class CustomWidget(Widget):
    ani_x = AniNumericProperty()
    ani_y = AniNumericProperty()
    ani_pos = AniMutableSequenceProperty()


w = CustomWidget()

# When the performance is important
w.x = ...
w.y = ...
w.pos = ...  # <- NOT RECOMMENDED
```

## Defining a new class just to add descriptors is ... cumbersome

`ani_property.install()`
