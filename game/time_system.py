class TimeSystem:
    def __init__(self):
        self.paused = False
        self.speed = 1

    def toggle_pause(self):
        self.paused = not self.paused

    def set_speed(self, speed):
        self.speed = max(0.5, min(8, speed))
