from pico2d import (
    clear_canvas,
    get_canvas_height,
    get_canvas_width,
    get_events,
    update_canvas,
)
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_SPACE, SDLK_r

import game_framework
from bird_flock import BirdFlock


flock: BirdFlock | None = None
paused = False


def handle_events() -> None:
    global paused

    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type != SDL_KEYDOWN:
            continue

        if event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        if event.key == SDLK_SPACE:
            paused = not paused
        elif event.key == SDLK_r and flock is not None:
            flock.reset()


def init() -> None:
    global flock, paused

    flock = BirdFlock(get_canvas_width(), get_canvas_height())
    paused = False


def pause() -> None:
    global paused
    paused = True


def resume() -> None:
    global paused
    paused = False


def finish() -> None:
    global flock
    flock = None


def update() -> None:
    if flock is not None and not paused:
        flock.update(game_framework.frame_time)


def render() -> None:
    clear_canvas()
    if flock is not None:
        flock.draw()
    update_canvas()
