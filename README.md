# AniProperty

A set of Python descriptors that animate numeric attributes of any object in a Kivy application.

```python
from kivy.uix.wiget import Widget
from ani_property import AniNumericProperty


class CustomWidget(Widget):
    ani_x = AniNumericProperty()
    ani_y = AniNumericProperty()


widget = CustomWidget(x=0, y=50)
widget.ani_x = 100  # -> animates 'widget.x' from 0 to 100
widget.ani_y = 100  # -> animates 'widget.y' from 50 to 200
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

You can also add a descriptor to a class outside of its definition. 

```python
from ani_property import AniNumericProperty, add_property

add_property(CustomWidget, 'ani_width', AniNumericProperty())
```

And you can animate a number sequence as well.

```python
from kivy.uix.label import Label
from ani_property import AniSequenceProperty


class CustomLabel(Label):
    ani_color = AniSequenceProperty(threshold=0.02)


label = CustomLabel(color=(1.0, 1.0, 1.0, 1.0))
label.ani_color = (1.0, 0.0, 0.0, 1.0)  # animates 'label.color' from white to red
```

It's advisable to use `AniNumericProperty` instead of `AniSequenceProperty` whenever possible due to performance reasons.
Thus, the following code:

```python
class CustomWidget(Widget):
    ani_x = AniNumericProperty()
    ani_y = AniNumericProperty()
    ani_width = AniNumericProperty()
    ani_height = AniNumericProperty()
```

is better than:

```python
class CustomWidget(Widget):
    ani_pos = AniSequenceProperty()
    ani_size = AniSequenceProperty()
```
