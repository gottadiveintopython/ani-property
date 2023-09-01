from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button

from ani_property import AniNumericProperty

KV_CODE = r'''
Widget:
    CustomButton:
        text: 'Kivy'
        on_touch_down:
            x, y = args[1].pos
            self.ani_x = x
            self.ani_y = y
'''


class CustomButton(Button):
    ani_x = AniNumericProperty()
    ani_y = AniNumericProperty()


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
