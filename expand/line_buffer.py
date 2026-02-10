class LineBuffer:
    def __init__(self, max_lines=10000):
        self.lines = []
        self.max_lines = max_lines
        self.auto_scroll = True

    def append(self, line):
        self.lines.append(line)
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[len(self.lines) - self.max_lines:]

    def total_lines(self):
        return len(self.lines)

    def get_visible(self, height, scroll_offset):
        start = max(0, scroll_offset)
        end = start + height
        return self.lines[start:end]

    def is_at_bottom(self, height, scroll_offset):
        return scroll_offset + height >= self.total_lines()
