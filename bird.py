from math import atan2, pi
from typing import Protocol


BIRD_LENGTH_CM = 15.0
PIXELS_PER_CM = 4.0
DISTANCE_PER_FLAP_CM = 81.0
FRAMES_PER_FLAP = 5
ANIMATION_FRAMES_PER_SECOND = 10.0
FLAP_DURATION_SECONDS = FRAMES_PER_FLAP / ANIMATION_FRAMES_PER_SECOND
FLIGHT_SPEED_PIXELS_PER_SECOND = (
    DISTANCE_PER_FLAP_CM * PIXELS_PER_CM / FLAP_DURATION_SECONDS
)

SHEET_COLUMNS = 5
SHEET_ROWS = 3
FLAP_POSE_INDICES = (0, 4, 7, 10, 13)
SPRITE_CONTENT_WIDTH_RATIO = 0.8


class SpriteSheet(Protocol):
    w: int
    h: int

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
    ) -> None: ...


class Bird:
    def __init__(
        self,
        sprite_sheet: SpriteSheet,
        x: float,
        y: float,
        heading_x: float,
        heading_y: float,
        animation_phase_seconds: float,
    ) -> None:
        self.sprite_sheet = sprite_sheet
        self.x = x
        self.y = y
        self.heading_x = heading_x
        self.heading_y = heading_y
        self.animation_phase_seconds = animation_phase_seconds

    def frame_index_at(self, elapsed_seconds: float) -> int:
        frame_number = int(
            (elapsed_seconds + self.animation_phase_seconds)
            * ANIMATION_FRAMES_PER_SECOND
            + 1e-9
        )
        return frame_number % FRAMES_PER_FLAP

    def draw(self, elapsed_seconds: float) -> None:
        pose_index = FLAP_POSE_INDICES[self.frame_index_at(elapsed_seconds)]
        column = pose_index % SHEET_COLUMNS
        row = pose_index // SHEET_COLUMNS

        left = column * self.sprite_sheet.w // SHEET_COLUMNS
        right = (column + 1) * self.sprite_sheet.w // SHEET_COLUMNS
        top = row * self.sprite_sheet.h // SHEET_ROWS
        bottom = (row + 1) * self.sprite_sheet.h // SHEET_ROWS
        source_width = right - left
        source_height = bottom - top

        heading = atan2(self.heading_y, self.heading_x)
        flip = ''
        rotation = heading
        if self.heading_x < 0:
            flip = 'h'
            rotation -= pi

        draw_width = (
            BIRD_LENGTH_CM * PIXELS_PER_CM / SPRITE_CONTENT_WIDTH_RATIO
        )
        draw_height = draw_width * source_height / source_width
        self.sprite_sheet.clip_composite_draw(
            left,
            self.sprite_sheet.h - bottom,
            source_width,
            source_height,
            rotation,
            flip,
            self.x,
            self.y,
            draw_width,
            draw_height,
        )
