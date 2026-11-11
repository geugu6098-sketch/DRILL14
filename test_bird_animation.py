import unittest

from bird import (
    ANIMATION_FRAMES_PER_SECOND,
    DISTANCE_PER_FLAP_CM,
    FLAP_DURATION_SECONDS,
    FLAP_POSE_INDICES,
    FLIGHT_SPEED_PIXELS_PER_SECOND,
    FRAMES_PER_FLAP,
    PIXELS_PER_CM,
    Bird,
)


class RecordingSpriteSheet:
    w = 918
    h = 506

    def __init__(self) -> None:
        self.draw_call: tuple[object, ...] | None = None

    def clip_composite_draw(
        self,
        left: int,
        bottom: int,
        width: int,
        height: int,
        rad: float,
        flip: str,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> None:
        self.draw_call = (left, bottom, width, height, rad, flip, x, y, w, h)


class BirdAnimationTests(unittest.TestCase):
    def test_flap_timing_and_distance_match_physical_specification(self) -> None:
        self.assertEqual(FRAMES_PER_FLAP, 5)
        self.assertEqual(ANIMATION_FRAMES_PER_SECOND, 10.0)
        self.assertEqual(FLAP_DURATION_SECONDS, 0.5)
        self.assertEqual(DISTANCE_PER_FLAP_CM, 81.0)
        self.assertEqual(PIXELS_PER_CM, 4.0)
        self.assertEqual(FLIGHT_SPEED_PIXELS_PER_SECOND, 648.0)
        self.assertEqual(
            FLIGHT_SPEED_PIXELS_PER_SECOND * FLAP_DURATION_SECONDS,
            DISTANCE_PER_FLAP_CM * PIXELS_PER_CM,
        )

    def test_animation_advances_on_elapsed_time_not_update_count(self) -> None:
        bird = Bird(RecordingSpriteSheet(), 0, 0, 1, 0, 0)

        self.assertEqual(
            [bird.frame_index_at(frame * 0.1) for frame in range(5)],
            [0, 1, 2, 3, 4],
        )
        self.assertEqual(bird.frame_index_at(FLAP_DURATION_SECONDS), 0)

    def test_sheet_pose_selection_uses_all_five_wingbeat_stages(self) -> None:
        self.assertEqual(FLAP_POSE_INDICES, (0, 4, 7, 10, 13))

    def test_first_pose_uses_pico2d_bottom_origin_source_coordinates(self) -> None:
        sprite_sheet = RecordingSpriteSheet()
        bird = Bird(sprite_sheet, 100, 200, 1, 0, 0)

        bird.draw(0)

        self.assertIsNotNone(sprite_sheet.draw_call)
        self.assertEqual(
            sprite_sheet.draw_call[:4],
            (0, 506 - 168, 183, 168),
        )

    def test_left_facing_bird_is_mirrored_without_reversing_its_heading(self) -> None:
        sprite_sheet = RecordingSpriteSheet()
        bird = Bird(sprite_sheet, 100, 200, -1, 0, 0)

        bird.draw(0)

        self.assertIsNotNone(sprite_sheet.draw_call)
        self.assertEqual(sprite_sheet.draw_call[5], 'h')
        self.assertAlmostEqual(sprite_sheet.draw_call[4], 0.0)


if __name__ == '__main__':
    unittest.main()
