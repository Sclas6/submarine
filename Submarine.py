class Submarine:
    def __init__(self, location: tuple):
        self.hp = 3
        self.location = location
        self.can_move = self.get_can_move()

    def hit(self):
        self.hp -= 1

    def get_can_move(self):
        loc_next = {(("UP", 1), (self.location[0] - 1, self.location[1])), (("DOWN", 1), (self.location[0] + 1, self.location[1])),
                    (("RIGHT", 1), (self.location[0], self.location[1] + 1)), (("LEFT", 1), (self.location[0], self.location[1] - 1)),
                    (("UP", 2), (self.location[0] - 2, self.location[1])), (("DOWN", 2), (self.location[0] + 2, self.location[1])),
                    (("RIGHT", 2), (self.location[0], self.location[1] + 2)), (("LEFT", 2), (self.location[0], self.location[1] - 2))}
        return {loc for loc in loc_next if loc[1][0] >= 0 and loc[1][0] < 5 and loc[1][1] >= 0 and loc[1][1] < 5}