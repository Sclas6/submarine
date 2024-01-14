from Sonar import Sonar
from Submarine import Submarine
from AI import AI, MapTools
from random import choice
import numpy as np
import copy

class Board:
    def __init__(self, size, ships):
        self.turn = 0
        self.sonar_enemy = Sonar(size, ships)
        self.sonar_ally = Sonar(size, ships)
        self.submarines = [Submarine(loc) for loc in AI.place_submarines()]
        self.map_ally = MapTools.gen_map_from_locs([sub.location for sub in self.submarines])
        self.hp_ally = 12
        self.hp_enemy = 12
        self.hit_count = 0
        self.pos_atk = None
        self.enemy_track = True
        self.cannot_enter = set()
        self.can_move = None
        self.can_atack = None
        self.update_map()

    def search_sub(self, loc: tuple) -> Submarine:
        for s in self.submarines:
            if s.location == loc:
                return s
        return None

    def remove_sub(self, loc: tuple):
        for i, s in enumerate(self.submarines):
            if s.location == loc:
                del self.submarines[i]
                break

    def update_map(self):
        for s in self.submarines:
            s.can_move = s.get_can_move()
        self.map_ally = MapTools.gen_map_from_locs([sub.location for sub in self.submarines])
        for sub in self.submarines:
            tmp = set()
            for mov_info in sub.can_move:
                if mov_info[0][1] == 1:
                    if mov_info[1] not in MapTools.get_pos(self.map_ally) and mov_info[1] not in self.cannot_enter:
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
                    if internal not in MapTools.get_pos(self.map_ally) and mov_info[1] not in MapTools.get_pos(self.map_ally) and internal not in self.cannot_enter and mov_info[1] not in self.cannot_enter:
                        tmp.add(mov_info)
            sub.can_move = tmp
        tmp = set()
        for s in self.submarines:
            for mov in s.can_move:
                tmp.add(mov[1])
        self.can_move = tmp
        self.can_atack = MapTools.can_atack(self.map_ally)

    def add_sinking(self, loc: tuple):
        self.cannot_enter.add(loc)
        self.sonar_ally.cannot_enter.add(loc)
        self.sonar_enemy.cannot_enter.add(loc)

    def atacked(self, loc: tuple):
        self.sonar_enemy.detect_obs(loc)
        sub = self.search_sub(loc)
        if sub != None:
            self.pos_atk = loc
            self.hit_count += 1
            sub.hit()
            self.hp_ally -= 1
            print(sub.hp)
            print(self.hp_ally)
            if sub.hp <= 0:
                self.sonar_ally.detect_sink(loc)
                self.hit_count = 0
                print("\tSINK")
                self.remove_sub(loc)
                self.add_sinking(loc)
                self.update_map()
            else:
                print("\tHIT")
                self.sonar_ally.detect_hit(loc)
        else:
            self.pos_atk = None
            self.hit_count = 0
            if loc in MapTools.can_atack(self.map_ally):
                print("\tOBS")
                self.sonar_ally.detect_obs(loc)
            else:
                print("\tMISS")
                self.sonar_ally.detect_miss(loc)

    def moved(self, mov_info: tuple):
        self.sonar_enemy.detect_mov(mov_info[0], mov_info[1])
        self.hit_count = 0

    def move_for_escape(self):
        m_atacked = 1
        ls_atacked = set()
        m_not_atacked = 1
        ls_not_atacked = set()
        for sub in self.submarines:
            for mov in sub.can_move:
                print("*", end="", flush=True)
                tmp = copy.deepcopy(self.sonar_ally)
                tmp.detect_mov(mov[0][0], mov[0][1])
                if sub.location == self.pos_atk:
                    m_atacked = min(m_atacked, np.max(tmp.map_pred))
                    ls_atacked.add((np.max(tmp.map_pred), sub.location, mov))
                else:
                    m_not_atacked = min(m_atacked, np.max(tmp.map_pred))
                    ls_not_atacked.add((np.max(tmp.map_pred), sub.location, mov))
        print("")
        ls_atacked = {n for n in ls_atacked if n[0] == m_atacked}
        ls_not_atacked = {n for n in ls_not_atacked if n[0] == m_not_atacked}

        if len(ls_atacked) == 0:
            n = choice(tuple(ls_not_atacked))
        elif len(ls_not_atacked) == 0:
            n = choice(tuple(ls_atacked))
        else:
            if self.enemy_track:
                if self.hit_count < 2:
                    n = choice(tuple(ls_not_atacked))
                else:
                    n = choice(tuple(ls_atacked))
                    self.enemy_track = False
            else:
                if self.hit_count < 2:
                    n = choice(tuple(ls_atacked))
                else:
                    n = choice(tuple(ls_not_atacked))
                    self.enemy_track = True
        sub = self.search_sub(n[1])
        sub.location = n[2][1]
        self.update_map()
        self.sonar_ally.detect_mov(n[2][0][0], n[2][0][1])

        return list(n[2][0])

    def move_for_atack(self, loc: tuple):
        if loc in [sub.location for sub in self.submarines]:
            sub = self.search_sub(loc)
            mov_info = choice(tuple([m for m in sub.can_move if m[0][1] == 1]))
            sub.location = mov_info[1]
            self.update_map()
            self.sonar_ally.detect_mov(mov_info[0][0], mov_info[0][1])

            return list(mov_info[0])
        else:
            '''mov_info = AI.move_to(self.submarines, loc)
            sub = self.search_sub(mov_info[1])
            sub.location = mov_info[2][1]
            self.update_map()
            self.sonar_ally.detect_mov(mov_info[2][0][0], mov_info[2][0][1])'''
            # print("BSF SEARCH")
            mov_info = AI.bfs(self.submarines, loc, self.cannot_enter)
            sub = self.search_sub(mov_info[0])
            sub.location = mov_info[1][1]
            self.update_map()
            self.sonar_ally.detect_mov(mov_info[1][0][0], mov_info[1][0][1])

            return list(mov_info[1][0])

    def atack(self, loc: tuple, result: str) -> bool:
        self.sonar_ally.detect_obs(loc)
        match result:
            case "SINK":
                self.hp_enemy -= 1
                self.sonar_enemy.detect_sink(loc)
                self.add_sinking(loc)
                self.update_map()
            case "HIT":
                self.hp_enemy -= 1
                self.sonar_enemy.detect_hit(loc)
            case "OBS":
                self.sonar_enemy.detect_obs(loc)
            case "MISS":
                self.sonar_enemy.detect_miss(loc)
            case x:
                print(f"ERROR: NOT COMMAND")
                return False

        return True


