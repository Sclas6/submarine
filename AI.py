from Sonar import Sonar
import numpy as np
from random import choice
from copy import deepcopy

class MapTools:
    def get_surroundings(loc: tuple) -> set:
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

    def can_move(map):
        ls = set()
        locs = MapTools.get_pos(map)
        for loc in locs:
            next_1 = [(loc[0], loc[1] + 1), (loc[0], loc[1] - 1),
                      (loc[0] + 1, loc[1]), (loc[0] - 1, loc[1])]
            ls |= {pos for pos in next_1 if pos[0] >= 0 and pos[0] < len(map) and pos[1] >= 0 and pos[1] < len(map) and pos not in locs}
            next_2 = [(loc[0], loc[1] + 2), (loc[0], loc[1] - 2),
                      (loc[0] + 2, loc[1]), (loc[0] - 2, loc[1])]
            for i, pos in enumerate(next_2):
                if next_1[i] not in locs and pos not in locs and pos[0] >= 0 and pos[0] < len(map) and pos[1] >= 0 and pos[1] < len(map):
                    ls.add(pos)
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
        tmp = Sonar(5, 4)
        for map in tmp.maps:
            m = max(m, len(MapTools.can_atack(map)) + len(MapTools.can_move(map)))
        ls = [map for map in tmp.maps if len(MapTools.can_atack(map)) + len(MapTools.can_move(map)) == m]
        return MapTools.get_pos(choice(ls))

    def move_to(subs, loc: tuple):
        area_atackable = MapTools.get_surroundings(loc)
        m = 100
        ls = set()
        for sub in subs:
            if sub.hp == 1 and sub != subs[-1]: continue
            for next in sub.can_move:
                for lll in area_atackable:
                    norm = np.linalg.norm(np.array(next[1]) - np.array(lll), ord=1)
                    m = min(m, norm)
                    ls.add((norm, sub.location, next))
                    #print(f"{next[1]} ({sub.location}_{next[0]}) to {lll}: {norm}")
        ls = {n for n in ls if n[0] == m}
        return choice(tuple(ls))

    def bfs(submarines, goal, cannot_enter):
        area_atackable = MapTools.get_surroundings(goal)
        map = MapTools.gen_map_from_locs([s.location for s in submarines])

        min_dist = 100
        min_route = []

        for area in area_atackable:
            if area in cannot_enter or area in MapTools.get_pos(map): continue
            subs = deepcopy(submarines)
            min_dist_for_area = 100
            min_route_for_area = []
            for sub in subs:
                ls_dist = np.full((len(map), len(map)), -1)
                ls_dist[sub.location] = 0
                ls_visited = np.full((len(map), len(map)), False)
                ls_visited[sub.location] = True
                prev = np.full((len(map), len(map)), None)
                queue = [sub.location]

                while len(queue) > 0:
                    q = queue.pop(0)
                    sub.location = q
                    sub.can_move = sub.get_can_move()
                    if q == area:
                        break
                    for mov_info in sub.can_move:
                        if mov_info[0][1] == 1:
                            if mov_info[1] not in MapTools.get_pos(map) and mov_info[1] not in cannot_enter and not ls_visited[mov_info[1]]:
                                queue.append(mov_info[1])
                                ls_visited[mov_info[1]] = True
                                ls_dist[mov_info[1]] = ls_dist[q] + mov_info[0][1]
                                prev[mov_info[1]] = q
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
                            if internal not in MapTools.get_pos(map) and mov_info[1] not in MapTools.get_pos(map) and internal not in cannot_enter and mov_info[1] not in cannot_enter and not ls_visited[mov_info[1]]:
                                queue.append(mov_info[1])
                                ls_visited[mov_info[1]] = True
                                ls_dist[mov_info[1]] = ls_dist[q] + mov_info[0][1]
                                prev[mov_info[1]] = q
                now = area
                ans = [now]
                while now != None:
                    now = prev[now]
                    if now != None: ans.insert(0, now)
                next = None
                for s in submarines:
                    if s.location == ans[0]:
                        for mov in s.can_move:
                            if mov[1] == ans[1]:
                                next = (s.location, mov)
                tmp = len(ans) if sub.hp != 1 else len(ans) + 10
                if tmp < min_dist_for_area:
                    min_dist_for_area = tmp
                    min_route_for_area = next
            if min_dist_for_area < min_dist:
                min_dist = min_dist_for_area
                min_route = min_route_for_area

        return min_route
