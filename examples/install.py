from kivy.app import App
from kivy.lang import Builder

import ani_property
ani_property.install()


KV_CODE = r'''
#:import randrange random.randrange

Widget:
    Button:
        text: 'Kivy'
        on_touch_down:
            self.ani_size = (randrange(50, 300), randrange(50, 300), )
            x, y = args[1].pos
            self.ani_x = x
            self.ani_y = y
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
