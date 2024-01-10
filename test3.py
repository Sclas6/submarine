from Sonner import Sonner
from Submarine import Submarine
from AI import AI, MapTools

SHIPS = 4
MAP_SIZE = 5
POS_Y = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
CAN_ATK = [(0, 1), (0, -1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1)]

is_atacked = False
turn = 0
sonner_enemy = Sonner(MAP_SIZE, SHIPS)
sonner_alies = Sonner(MAP_SIZE, SHIPS)

hp_enemy = 12
hp_alies = 12

# Initialize
submarines = [Submarine(loc) for loc in AI.place_submarines()]
for sub in submarines:
    print(MapTools.yx2loc(sub.location))
map_alies = MapTools.gen_map_from_locs([sub.location for sub in submarines])

print(MapTools.gen_map_from_locs([sub.location for sub in submarines]))

def gen_can_move(subs, map):
    for sub in subs:
        tmp = set()
        for mov_info in sub.can_move:
            if mov_info[0][1] == 1:
                if mov_info[1] not in MapTools.get_pos(map):
                    tmp.add(mov_info)
            else:
                internal = list(sub.location)
                match mov_info[0][0]:
                    case "UP":
                        internal[0] -= 1
                    case "DOWN":
                        internal[0] += 1
                    case "LEFT":
                        internal[1] -= 1
                    case "RIGHT":
                        internal[1] += 1
                internal = tuple(internal)
                print(f"loc: {sub.location} mov: {mov_info} inter: {internal}")
                if internal not in MapTools.get_pos(map):
                    tmp.add(mov_info)
        sub.can_move = tmp


gen_can_move(submarines, map_alies)

for sub in submarines:
    print(sub.location)
    print(sub.can_move)