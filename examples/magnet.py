from functools import partial
from random import shuffle
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder

import ani_property
ani_property.install()


KV_CODE = r'''
GridLayout:
    rows: 4
    cols: 4
    padding: 20
    spacing: 20
'''


def shuffle_children(widget, dt):
    children = widget.children[:]
    widget.clear_widgets()
    shuffle(children)
    for c in children:
        widget.add_widget(c)


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        from kivy.uix.button import Button
        from ani_property import AniMagnet

        grid = self.root
        for i in range(grid.rows * grid.cols):
            label = Button(text=str(i), font_size=50, opacity=0.5)
            magnet = AniMagnet()
            magnet.add_widget(label)
            grid.add_widget(magnet)

        Clock.schedule_interval(partial(shuffle_children, grid), 3)


if __name__ == '__main__':
    SampleApp().run()
