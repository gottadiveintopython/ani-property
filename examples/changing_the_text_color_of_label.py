from kivy.utils import get_random_color
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label

from ani_property import AniMutableSequenceProperty


class CustomLabel(Label):
    ani_color = AniMutableSequenceProperty(threshold=0.02, speed=2.0)


class SampleApp(App):
    def build(self):
        return CustomLabel(text='Hello Kivy', font_size='120sp')

    def on_start(self):
        Clock.schedule_interval(self.change_text_color, 2)

    def change_text_color(self, dt):
        self.root.ani_color = get_random_color()


if __name__ == '__main__':
    SampleApp().run()
