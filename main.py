from pico2d import close_canvas, open_canvas
import game_framework

import play_mode as start_mode


open_canvas(900, 1600)
game_framework.run(start_mode)
close_canvas()
