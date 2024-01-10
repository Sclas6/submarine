import numpy as np
import itertools as it

POS_Y = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
CAN_ATK = [(0, 1), (0, -1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1)]

class Sonar:
    def __init__(self, size: int ,ships: int):
        self.size = size
        self.ships = ships
        list_xy = range(size)
        compounds = list(it.product(list_xy, repeat=2))
        self.poses_pred = np.array(list(it.combinations(compounds, ships)))
        self.maps = self.gen_maps()
        self.map_pred = sum(self.maps) / len(self.maps)

    def gen_maps(self):
        maps = []
        for poses in self.poses_pred:
            copied = np.zeros((self.size, self.size))
            for c in poses:
                copied[c[0], c[1]] = 1
            maps.append(copied)
        self.maps = np.array(maps)
        self.map_pred = sum(self.maps) / len(self.maps)
        self.gen_pred_index()
        return np.array(maps)

    def gen_pred_index(self):
        tmp = []
        count = 0
        copied = np.copy(self.map_pred)
        while(True):
            max = np.max(copied)
            pos_max = list(zip(np.where(copied==max)[0], np.where(copied==max)[1]))
            for pos in pos_max:
                tmp.append(pos)
                copied[pos[0]][pos[1]] = -1
            count += len(pos_max)
            if count >= self.size**2: break
        self.index_pred = tmp

    def detect_mov(self, dir: int, i: int):
        tmp = set()
        for poses in self.poses_pred:
            for j in range(len(poses)):
                moved = [list(pos) for pos in poses]
                match dir:
                    case "UP":
                        moved[j][0] -= i
                        if moved[j][0] < 0: continue
                    case "DOWN":
                        moved[j][0] += i
                        if moved[j][0] >= self.size: continue
                    case "RIGHT":
                        moved[j][1] += i
                        if moved[j][1] >= self.size: continue
                    case "LEFT":
                        moved[j][1] -= i
                        if moved[j][1] < 0: continue
                moved.sort()
                moved = set([tuple(p) for p in moved])
                if len(moved) != self.ships: continue
                tmp.add(tuple(moved))
        self.poses_pred = np.array(list(tmp))
        self.gen_maps()

    def detect_obs(self, pos_obs: tuple):
        tmp = []
        pos_possibility = set([tuple(p) for p in list(pos_obs) + np.array(CAN_ATK) if p[0] >= 0 and p[0] < self.size and p[1] >= 0 and p[1] < self.size])
        for poses in self.poses_pred:
            poses_set = set([tuple(p) for p in poses])
            possible = False
            for poses_obs in pos_possibility:
                if poses_obs in poses_set and pos_obs not in poses_set:
                    possible = True
            if possible: tmp.append(poses)
        self.poses_pred = np.array(tmp)
        self.gen_maps()

    def detect_hit(self, pos_hit: tuple):
        tmp = []
        for poses in self.poses_pred:
            poses_set = set([tuple(p) for p in poses])
            possible = False
            if pos_hit in poses_set:
                possible = True
            if possible: tmp.append(poses)
        self.poses_pred = np.array(tmp)
        self.gen_maps()

    def detect_miss(self, pos_miss: tuple):
        tmp = []
        pos_possibility = set([tuple(p) for p in list(pos_miss) + np.array(CAN_ATK) if p[0] >= 0 and p[0] < self.size and p[1] >= 0 and p[1] < self.size])
        pos_possibility.add(pos_miss)
        for poses in self.poses_pred:
            poses_set = set([tuple(p) for p in poses])
            possible = True
            for poses_obs in pos_possibility:
                if poses_obs in poses_set:
                    possible = False
            if possible: tmp.append(poses)
        self.poses_pred = np.array(tmp)
        self.gen_maps()

    def detect_sink(self, pos_sink: tuple):
        tmp = []
        self.detect_hit(pos_sink)
        self.ships -= 1
        for poses in self.poses_pred:
            poses = np.delete(poses, np.where(np.all(poses == pos_sink, axis=1))[0], axis=0)
            tmp.append(poses)
        self.poses_pred = np.array(tmp)
        self.gen_maps()