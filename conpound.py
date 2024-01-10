import numpy as np
import itertools as it

SHIPS = 4
MAP_SIZE = 5

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

def sonner_mov(poses_list: list, dir: int, i: int):
    tmp = []
    for pos in poses_list:
        for j in range(len(pos)):
            moved = [[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]]
            match dir:
                case UP:
                    moved[j][0] -= i
                    moved.sort()
                    if moved[0][0] < 0 or moved[1][0] < 0 or moved[2][0] < 0 or moved[3][0] < 0 or len(np.unique(moved, axis=0)) != 4 or moved in tmp: continue
                    tmp.append(moved)
    return tmp

def gen_maps(poses_pred: list):
    maps = []
    for poses in poses_pred:
        copied = enemy_map.copy()
        for c in poses:
            copied[c[0], c[1]] = 1
        maps.append(copied)
    return maps

enemy_map = np.zeros((MAP_SIZE, MAP_SIZE))

#print((np.random.choice(5), np.random.choice(5)))

# あるマスに潜水艦がいる確率
# Aがいる確率+Bがいる確率+Cがいる確率+Dがいる確率

# 全通り抽出
list_xy = range(MAP_SIZE)
compounds = np.array(list(it.product(list_xy, repeat=2)))

pos_pred = np.array(list(it.combinations(compounds, SHIPS)))
maps = gen_maps(pos_pred)


print(len(pos_pred))
print(sum(maps) / len(maps))
print(sum(maps))

for i in range(1):
    pos_pred = sonner_mov(pos_pred, UP, 1)
maps = gen_maps(pos_pred)
print(len(pos_pred))
print(sum(maps) / len(maps))
print(sum(maps))

