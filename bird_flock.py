from math import atan2, cos, hypot, pi, sin

from pico2d import load_image

from bird import (
    BIRD_LENGTH_CM,
    FLAP_DURATION_SECONDS,
    FLIGHT_SPEED_PIXELS_PER_SECOND,
    PIXELS_PER_CM,
    Bird,
)


BIRD_COUNT = 10
INITIAL_SPACING_CM = BIRD_LENGTH_CM * 2
SEPARATION_DISTANCE_CM = BIRD_LENGTH_CM * 2
NEIGHBOR_DISTANCE_CM = 180.0
SEPARATION_WEIGHT = 4.0
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 0.6
HEADING_WEIGHT = 1.5
MAX_TURN_RATE_RADIANS_PER_SECOND = pi / 2


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

        new_headings = [
            self._next_heading(bird, delta_time)
            for bird in self.birds
        ]
        self.elapsed_seconds += delta_time
        distance = FLIGHT_SPEED_PIXELS_PER_SECOND * delta_time
        for bird, (heading_x, heading_y) in zip(self.birds, new_headings):
            bird.heading_x = heading_x
            bird.heading_y = heading_y
            bird.x = (bird.x + bird.heading_x * distance) % self.canvas_width
            bird.y = (bird.y + bird.heading_y * distance) % self.canvas_height

    def _next_heading(self, bird: Bird, delta_time: float) -> tuple[float, float]:
        separation_x = 0.0
        separation_y = 0.0
        alignment_x = 0.0
        alignment_y = 0.0
        cohesion_x = 0.0
        cohesion_y = 0.0
        neighbor_count = 0
        separation_distance = SEPARATION_DISTANCE_CM * PIXELS_PER_CM
        neighbor_distance = NEIGHBOR_DISTANCE_CM * PIXELS_PER_CM

        for other in self.birds:
            if other is bird:
                continue

            offset_x = (
                other.x - bird.x + self.canvas_width / 2
            ) % self.canvas_width - self.canvas_width / 2
            offset_y = (
                other.y - bird.y + self.canvas_height / 2
            ) % self.canvas_height - self.canvas_height / 2
            distance = hypot(offset_x, offset_y)
            if distance == 0 or distance > neighbor_distance:
                continue

            neighbor_count += 1
            alignment_x += other.heading_x
            alignment_y += other.heading_y
            cohesion_x += offset_x
            cohesion_y += offset_y

            if distance < separation_distance:
                separation_strength = (
                    separation_distance - distance
                ) / separation_distance
                separation_x -= offset_x / distance * separation_strength
                separation_y -= offset_y / distance * separation_strength

        if neighbor_count:
            alignment_x /= neighbor_count
            alignment_y /= neighbor_count
            cohesion_x /= neighbor_count
            cohesion_y /= neighbor_count

        separation_x, separation_y = self._unit_vector(
            separation_x, separation_y
        )
        alignment_x, alignment_y = self._unit_vector(
            alignment_x, alignment_y
        )
        cohesion_x, cohesion_y = self._unit_vector(
            cohesion_x, cohesion_y
        )

        target_x = (
            bird.heading_x * HEADING_WEIGHT
            + separation_x * SEPARATION_WEIGHT
            + alignment_x * ALIGNMENT_WEIGHT
            + cohesion_x * COHESION_WEIGHT
        )
        target_y = (
            bird.heading_y * HEADING_WEIGHT
            + separation_y * SEPARATION_WEIGHT
            + alignment_y * ALIGNMENT_WEIGHT
            + cohesion_y * COHESION_WEIGHT
        )
        target_x, target_y = self._unit_vector(target_x, target_y)

        current_angle = atan2(bird.heading_y, bird.heading_x)
        target_angle = atan2(target_y, target_x)
        angle_delta = (target_angle - current_angle + pi) % (2 * pi) - pi
        max_turn = MAX_TURN_RATE_RADIANS_PER_SECOND * delta_time
        turn = max(-max_turn, min(max_turn, angle_delta))
        next_angle = current_angle + turn
        return cos(next_angle), sin(next_angle)

    @staticmethod
    def _unit_vector(x: float, y: float) -> tuple[float, float]:
        length = hypot(x, y)
        if length == 0:
            return 0.0, 0.0
        return x / length, y / length

    def draw(self) -> None:
        for bird in self.birds:
            bird.draw(self.elapsed_seconds)
