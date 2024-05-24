
class brect:
    """Specify bounding box in absolute curse coordinates."""

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def bottom(self) -> int:
        """Return the y coordinate of the last line"""
        return self.y + self.h - 1

    def right(self) -> int:
        """Return the x coordinate of the rightmost part of the line"""
        return self.x + self.w - 1


    def colliding(self, rect) -> bool:
        """Whether this box is overlapping with another bounding box."""

        return not (self.x + self.w <= rect.x or
                    self.x >= rect.x + rect.w or
                    self.y + self.h <= rect.y or
                    self.y >= rect.y + rect.h)


    def copy(self):
        return brect(self.x, self.y, self.w, self.h)


    @staticmethod
    def calculate_alignment_offset(rect, container_rect, alignment: tuple[int, int]):
        """
        Returns an offset (o_x, o_y) such that:

            x = rect.x + o_x
            y = rect.y + o_y

        correctly aligns `rect` with `container_rect`. 

        Alignment is passed as a tuple (o_h, o_v) such that:

            (-1, -1) is topleft alignment
            (0, -1) is top alignment
            (1, -1) is topright alignment

            (-1, 0) is left alignment
            (0, 0) is middle alignment
            (1, 0) is right alignment

            (-1, 1) is bottomleft alignment
            (0, 1) is bottom alignment
            (1, 1) is bottomright alignment
        """

        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        offset_x, offset_y = 0, 0

        if alignment[1] == -1:
            offset_y = container_rect.y - y
        elif alignment[1] == 0:
            offset_y = container_rect.y + container_rect.h // 2 - h // 2 - y
        elif alignment[1] == 1:
            offset_y = container_rect.y + container_rect.h - y - h

        if alignment[0] == -1:
            offset_x = container_rect.x - x
        elif alignment[0] == 0:
            offset_x = container_rect.x + container_rect.w // 2 - w // 2 - x
        elif alignment[0] == 1:
            offset_x = container_rect.x + container_rect.w - x - w

        
        return offset_x, offset_y




