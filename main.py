from pico2d import open_canvas, delay, close_canvas
import game_framework

import play_mode as start_mode
import boy


# Keep the game running if a state omits its render method.
_state_draw = next(
	(
		value.draw
		for value in vars(boy).values()
		if isinstance(value, type)
		and value.__name__ != 'Run'
		and callable(getattr(value, 'draw', None))
	),
	lambda self, character: None,
)
if hasattr(boy, 'Run') and not hasattr(boy.Run, 'draw'):
	boy.Run.draw = _state_draw

open_canvas(1600, 600)
game_framework.run(start_mode)
close_canvas()
