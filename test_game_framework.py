import unittest
from unittest.mock import patch

import game_framework


class OneFrameMode:
    def __init__(self) -> None:
        self.observed_delta_time = -1.0
        self.finished = False

    def init(self) -> None:
        pass

    def handle_events(self) -> None:
        pass

    def update(self) -> None:
        self.observed_delta_time = game_framework.frame_time
        game_framework.quit()

    def render(self) -> None:
        pass

    def finish(self) -> None:
        self.finished = True


class GameFrameworkTimingTests(unittest.TestCase):
    def run_one_frame(self, start: float, current: float) -> OneFrameMode:
        mode = OneFrameMode()
        with patch(
            'game_framework.time.perf_counter',
            side_effect=(start, current),
        ):
            game_framework.run(mode)
        return mode

    def test_delta_time_is_available_during_the_update(self) -> None:
        mode = self.run_one_frame(10.0, 10.05)

        self.assertAlmostEqual(mode.observed_delta_time, 0.05)
        self.assertTrue(mode.finished)

    def test_long_frame_delta_is_capped(self) -> None:
        mode = self.run_one_frame(10.0, 11.0)

        self.assertEqual(mode.observed_delta_time, game_framework.MAX_FRAME_TIME)


if __name__ == '__main__':
    unittest.main()
