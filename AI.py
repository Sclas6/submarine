from Sonner import Sonner
import numpy as np
from random import choice

class MapTools:
    def get_surroundings(loc: tuple):
        ls = set()
        ls.add((loc[0] - 1, loc[1]))
        ls.add((loc[0] - 1, loc[1] - 1))
        ls.add((loc[0] - 1, loc[1] + 1))
        ls.add((loc[0], loc[1] - 1))
        ls.add((loc[0], loc[1] + 1))
        ls.add((loc[0] + 1, loc[1]))
        ls.add((loc[0] + 1, loc[1] - 1))
        ls.add((loc[0] + 1, loc[1] + 1))
        ls = {elem for elem in ls if elem[0] >= 0 and elem[0] < 5 and elem[1] >= 0 and elem[1] < 5}
        return ls

    def can_atack(map):
        ls = set()
        for y, a in enumerate(map):
            for x, _ in enumerate(a):
                if map[y][x] == 1:
                    ls |= MapTools.get_surroundings((y, x))
        ls = {elem for elem in ls if map[elem[0]][elem[1]] == 0}
        return ls

    def get_pos(map):
        ls = set()
        for y, a in enumerate(map):
            for x, _ in enumerate(a):
                if map[y][x] == 1:
                    ls.add((y, x))
        return ls

    def yx2loc(loc: tuple):
        match loc[0]:
            case 0:
                return ('A', loc[1] + 1)
            case 1:
                return ('B', loc[1] + 1)
            case 2:
                return ('C', loc[1] + 1)
            case 3:
                return ('D', loc[1] + 1)
            case 4:
                return ('E', loc[1] + 1)

    def gen_map_from_locs(locs):
        tmp = np.zeros((5, 5))
        for loc in locs:
            tmp[loc[0]][loc[1]] = 1
        return tmp



class AI:
    def place_submarines():
        m = 0
        tmp = Sonner(5, 4)
        for map in tmp.maps:
            m = max(m, len(MapTools.can_atack(map)))
        ls = [map for map in tmp.maps if len(MapTools.can_atack(map)) == m]
        return MapTools.get_pos(choice(ls))
        '''m = 100
        tmp = Sonner(5, 4)
        for map in tmp.maps:
            m = min(m, len(MapTools.can_atack(map)))
        ls = [map for map in tmp.maps if len(MapTools.can_atack(map)) == m]
        return MapTools.get_pos(choice(ls))'''
    def move_to(subs, loc: tuple):
        area_atackable = MapTools.get_surroundings(loc)
        m = 100
        ls = set()
        for sub in subs:
            for next in sub.can_move:
                for lll in area_atackable:
                    norm = np.linalg.norm(np.array(next[1]) - np.array(lll), ord=1)
                    m = min(m, norm)
                    ls.add((norm, sub.location, next))
                    #print(f"{next[1]} ({sub.location}_{next[0]}) to {lll}: {norm}")
        ls = {n for n in ls if n[0] == m}
        return choice(tuple(ls))