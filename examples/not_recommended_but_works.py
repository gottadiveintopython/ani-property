from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button

from ani_property import AniSequenceProperty

KV_CODE = r'''
Widget:
    CustomButton:
        text: 'Kivy'
        on_touch_down: self.ani_pos = args[1].pos
'''


class CustomButton(Button):
    ani_pos = AniSequenceProperty()


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
