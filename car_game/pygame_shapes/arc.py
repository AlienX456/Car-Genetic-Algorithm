from pygame import Rect

class Arc:

    def __init__(self, left, top, width, height, start_angle, stop_angle, arc_width):
        self.rect = Rect(left, top, width, height)
        self.start_angle = start_angle
        self.stop_angle = stop_angle
        self.arc_width = arc_width
