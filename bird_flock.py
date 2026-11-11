from math import cos, pi, sin

from pico2d import load_image

from bird import (
    BIRD_LENGTH_CM,
    FLAP_DURATION_SECONDS,
    FLIGHT_SPEED_PIXELS_PER_SECOND,
    PIXELS_PER_CM,
    Bird,
)


BIRD_COUNT = 10
INITIAL_SPACING_CM = 30.0


class BirdFlock:
    def __init__(
        self,
        canvas_width: int = 900,
        canvas_height: int = 1600,
        bird_count: int = BIRD_COUNT,
    ) -> None:
        if canvas_width <= 0 or canvas_height <= 0:
            raise ValueError('Canvas dimensions must be positive.')
        if bird_count <= 0:
            raise ValueError('A flock must contain at least one bird.')

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.sprite_sheet = load_image('bird_animation.png')
        self.birds: list[Bird] = []
        self.elapsed_seconds = 0.0
        self.reset(bird_count)

    def reset(self, bird_count: int = BIRD_COUNT) -> None:
        if bird_count <= 0:
            raise ValueError('A flock must contain at least one bird.')

        self.elapsed_seconds = 0.0
        if bird_count == 1:
            formation_radius = 0.0
        else:
            spacing_pixels = INITIAL_SPACING_CM * PIXELS_PER_CM
            formation_radius = spacing_pixels / (2 * sin(pi / bird_count))

        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        self.birds = []
        for index in range(bird_count):
            angle = 2 * pi * index / bird_count
            self.birds.append(
                Bird(
                    self.sprite_sheet,
                    center_x + formation_radius * cos(angle),
                    center_y + formation_radius * sin(angle),
                    1.0,
                    0.0,
                    FLAP_DURATION_SECONDS * index / bird_count,
                )
            )

    def update(self, delta_time: float) -> None:
        if delta_time < 0:
            raise ValueError('Delta time must not be negative.')
        if delta_time == 0:
            return

        self.elapsed_seconds += delta_time
        distance = FLIGHT_SPEED_PIXELS_PER_SECOND * delta_time
        for bird in self.birds:
            bird.x = (bird.x + bird.heading_x * distance) % self.canvas_width
            bird.y = (bird.y + bird.heading_y * distance) % self.canvas_height

    def draw(self) -> None:
        for bird in self.birds:
            bird.draw(self.elapsed_seconds)
