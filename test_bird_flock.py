import math
import unittest
from unittest.mock import patch

from bird import FLAP_DURATION_SECONDS, FLIGHT_SPEED_PIXELS_PER_SECOND
from bird_flock import (
    BIRD_COUNT,
    INITIAL_SPACING_CM,
    PIXELS_PER_CM,
    BirdFlock,
)


class FakeSpriteSheet:
    w = 918
    h = 506


class BirdFlockTests(unittest.TestCase):
    def create_flock(
        self,
        bird_count: int = BIRD_COUNT,
        canvas_width: int = 2000,
        canvas_height: int = 2000,
    ) -> BirdFlock:
        with patch('bird_flock.load_image', return_value=FakeSpriteSheet()):
            return BirdFlock(canvas_width, canvas_height, bird_count)

    def test_default_flock_contains_ten_evenly_spaced_birds(self) -> None:
        flock = self.create_flock()

        self.assertEqual(len(flock.birds), 10)
        first, second = flock.birds[:2]
        initial_distance = math.hypot(
            second.x - first.x,
            second.y - first.y,
        )
        self.assertAlmostEqual(
            initial_distance,
            INITIAL_SPACING_CM * PIXELS_PER_CM,
        )

    def test_one_flap_covers_exactly_81_cm_of_straight_path(self) -> None:
        flock = self.create_flock(bird_count=1, canvas_width=1000)
        bird = flock.birds[0]
        start_x = bird.x

        flock.update(FLAP_DURATION_SECONDS)

        self.assertAlmostEqual(
            bird.x - start_x,
            FLIGHT_SPEED_PIXELS_PER_SECOND * FLAP_DURATION_SECONDS,
        )
        self.assertAlmostEqual(bird.y, 1000)

    def test_close_birds_steer_apart_and_keep_unit_heading(self) -> None:
        flock = self.create_flock(bird_count=2)
        first, second = flock.birds
        first.x, first.y = 500, 500
        second.x, second.y = 550, 500
        first.heading_x = second.heading_x = 1.0
        first.heading_y = second.heading_y = 0.0
        initial_distance = 50.0

        flock.update(0.1)

        final_distance = math.hypot(second.x - first.x, second.y - first.y)
        self.assertGreater(final_distance, initial_distance)
        for bird in flock.birds:
            self.assertAlmostEqual(
                math.hypot(bird.heading_x, bird.heading_y),
                1.0,
            )

    def test_crossing_canvas_edge_wraps_without_stopping_flight(self) -> None:
        flock = self.create_flock(bird_count=1, canvas_width=1000)
        bird = flock.birds[0]
        bird.x = 990

        flock.update(0.1)

        self.assertAlmostEqual(
            bird.x,
            (990 + FLIGHT_SPEED_PIXELS_PER_SECOND * 0.1) % 1000,
        )

    def test_negative_delta_time_is_rejected(self) -> None:
        flock = self.create_flock(bird_count=1)

        with self.assertRaises(ValueError):
            flock.update(-0.1)


if __name__ == '__main__':
    unittest.main()
