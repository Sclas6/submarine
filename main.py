from Sonar import Sonar
from Submarine import Submarine
from AI import AI, MapTools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import copy
from random import choice

cmap = plt.cm.Greys
grey_alpha = cmap(np.arange(cmap.N))
grey_alpha[:,-1] = np.linspace(0, 1, cmap.N)
grey_alpha = ListedColormap(grey_alpha)

cannot_enter = set()

def gen_can_move(subs, map):
    for sub in subs:
        tmp = set()
        for mov_info in sub.can_move:
            '''if mov_info[1] in cannot_enter:
                continue'''
            if mov_info[0][1] == 1:
                if mov_info[1] not in MapTools.get_pos(map) and mov_info[1] not in cannot_enter:
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
                if internal not in MapTools.get_pos(map) and mov_info[1] not in MapTools.get_pos(map) and internal not in cannot_enter and mov_info[1] not in cannot_enter:
                    tmp.add(mov_info)
        sub.can_move = tmp

SHIPS = 4
MAP_SIZE = 5
POS_Y = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}

is_atacked = False
turn = 0
sonner_enemy = Sonar(MAP_SIZE, SHIPS)
sonner_allies = Sonar(MAP_SIZE, SHIPS)

hp_enemy = 12
hp_allies = 12

hit_count = 0
enemy_track = True

# Initialize
submarines = [Submarine(loc) for loc in AI.place_submarines()]
for sub in submarines:
    print(MapTools.yx2loc(sub.location))
map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
gen_can_move(submarines, map_allies)

fig = plt.figure()

print(MapTools.gen_map_from_locs([sub.location for sub in submarines]))

tmp = input("IS FIRST? (Y/N): ")
if tmp == "Y": turn += 1
while(True):
    if turn % 2 == 0:
        if True:
        #try:
            confirm = False
            while not confirm:
                command_raw = input("ENEMY ACTION?: ").split()
                command = command_raw[0]
                token_list = command_raw[1:]
                print(f"COMMAND: {command}\nTOKENS: {[token for token in token_list]}")
                tmp = input("CORRECT? (Y/N): ")
                confirm = True if tmp == "Y" else False

            match command:
                case "ATK":
                    atk_position = (POS_Y.get(token_list[0]), int(token_list[1]) - 1)
                    sonner_enemy.detect_obs(atk_position)
                    breaked = False
                    for sub in submarines:
                        if atk_position == sub.location:
                            hit_count += 1
                            sub.hit()
                            hp_allies -= 1
                            print(f"HP: {sub.hp}")
                            print(f"HP: {hp_allies}")
                            if sub.hp == 0:
                                print("\tSINK")
                                sonner_allies.detect_sink(atk_position)
                                hit_count = 0
                                for i, s in enumerate(submarines):
                                    if atk_position == s.location:
                                        del submarines[i]
                                cannot_enter.add(atk_position)
                                sonner_allies.cannot_enter.add(atk_position)
                                sonner_enemy.cannot_enter.add(atk_position)
                                map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
                                gen_can_move(submarines, map_allies)
                            else:
                                print("\tHIT")
                                sonner_allies.detect_hit(atk_position)
                            breaked = True
                            break
                    if not breaked:
                        hit_count = 0
                        if atk_position in MapTools.can_atack(map_allies):
                            print("\tOBS")
                            sonner_allies.detect_obs(atk_position)
                        else:
                            sonner_allies.detect_miss(atk_position)
                            print("\tMISS")
                case "MOV":
                    sonner_enemy.detect_mov(token_list[0], int(token_list[1]))
                    hit_count = 0
                case "EXIT":
                    exit()
                case x:
                    print(f"ERROR: NOT COMMAND")
                    continue
        #except Exception as e:
        #    print(f"ERROR: {e} {sys.exc_info()}")
        #    continue
    else:
        command = ""
        token_list = []
        movable = 0
        for s in submarines:
            movable += len(s.can_move)
        if movable == 0:
            for pos in sonner_enemy.index_pred:
                if pos in MapTools.can_atack(map_allies):
                    command = "ATK"
                    token_list = list(MapTools.yx2loc(pos))
                    break
        else:
            if hit_count != 0:
                # ATK
                if True:
                    for pos in sonner_enemy.index_pred:
                        if sonner_enemy.map_pred[pos[0]][pos[1]] == 1 and pos in MapTools.can_atack(map_allies):
                            command = "ATK"
                            token_list = list(MapTools.yx2loc(pos))
                            break
                if command != "ATK":
                    command = "MOV"
                    m_atacked = 1
                    ls_atacked = set()
                    m_not_atacked = 1
                    ls_not_atacked = set()
                    for sub in submarines:
                        for mov in sub.can_move:
                            print("*", end="", flush=True)
                            tmp = copy.deepcopy(sonner_allies)
                            tmp.detect_mov(mov[0][0], mov[0][1])
                            if sub.location == atk_position:
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
                        if enemy_track:
                            if hit_count < 2:
                                n = choice(tuple(ls_not_atacked))
                            else:
                                n = choice(tuple(ls_atacked))
                                enemy_track = False
                        else:
                            if hit_count < 2:
                                n = choice(tuple(ls_atacked))
                            else:
                                n = choice(tuple(ls_not_atacked))
                                enemy_track = True
                    token_list = list(n[2][0])
                    for sub in submarines:
                        if sub.location == n[1]:
                            sub.location = n[2][1]
                            sub.can_move = sub.get_can_move()
                            map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
                            gen_can_move(submarines, map_allies)
                            sonner_allies.detect_mov(n[2][0][0], n[2][0][1])
                    #print(map_alies)

            else:
                # ATK
                command = "ATK"
                for loc in sonner_enemy.index_pred:
                    if loc in MapTools.can_atack(map_allies):
                        loc_atk = MapTools.yx2loc(loc)
                        token_list = list(loc_atk)
                        break
                    else:
                        if sonner_enemy.map_pred[loc[0]][loc[1]] >= 0.5:
                            if loc in [sub.location for sub in submarines]:
                                command = "MOV"
                                for sub in submarines:
                                    if loc == sub.location:
                                        #mov_info = choice(tuple(sub.can_move))
                                        mov_info = choice(tuple([m for m in sub.can_move if m[0][1] == 1]))
                                        token_list = list(mov_info[0])
                                        sub.location = mov_info[1]
                                        sub.can_move = sub.get_can_move()
                                        gen_can_move(submarines, map_allies)
                                        map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
                                        sonner_allies.detect_mov(mov_info[0][0], mov_info[0][1])
                                        break
                                break
                            else:
                                command = "MOV"
                                mov_info = AI.move_to(submarines, loc)
                                token_list = list(mov_info[2][0])
                                for sub in submarines:
                                    if sub.location == mov_info[1]:
                                        sub.location = mov_info[2][1]
                                        sub.can_move = sub.get_can_move()
                                        map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
                                        gen_can_move(submarines, map_allies)
                                        sonner_allies.detect_mov(mov_info[2][0][0], mov_info[2][0][1])
                                        break
                                break

        print(f"{command} {token_list[0]} {token_list[1]}")

        if command == "ATK":
            pos_atk = (POS_Y.get(token_list[0]), int(token_list[1]) - 1)
            print(pos_atk)
            sonner_allies.detect_obs(pos_atk)
            confirm = False
            while not confirm:
                result = input("Result? : ").split()[0]
                match result:
                    case "SINK":
                        hp_enemy -= 1
                        sonner_enemy.detect_sink(pos_atk)
                        cannot_enter.add(pos_atk)
                        sonner_allies.cannot_enter.add(pos_atk)
                        sonner_enemy.cannot_enter.add(pos_atk)
                        gen_can_move(submarines, map_allies)
                        confirm = True
                    case "HIT":
                        hp_enemy -= 1
                        sonner_enemy.detect_hit(pos_atk)
                        confirm = True
                    case "OBS":
                        sonner_enemy.detect_obs(pos_atk)
                        confirm = True
                    case "MISS":
                        sonner_enemy.detect_miss(pos_atk)
                        confirm = True
                    case x:
                        print(f"ERROR: NOT COMMAND")
                        continue
    '''print(sonner_enemy.map_pred)
    print(sonner_enemy.index_pred)
    print(sonner_allies.map_pred)
    print(sonner_allies.index_pred)
    print(map_allies)'''
    fig.clear()
    ax1 = fig.add_subplot(221)
    ax1.pcolor(np.flipud(sonner_enemy.map_pred), cmap=plt.cm.Greens, vmin=0, vmax=1)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax2.pcolor(np.flipud(MapTools.gen_map_from_locs(cannot_enter)), cmap=plt.cm.Reds, vmin=0, vmax=1)
    can_move = set()
    for s in submarines:
        for mov in s.can_move:
            can_move.add(mov[1])
    #print(can_move)
    ax3.pcolor(np.flipud(MapTools.gen_map_from_locs(can_move)), cmap=plt.cm.Blues, vmin=0, vmax=1)
    ax2.pcolor(np.flipud(map_allies), cmap=grey_alpha, vmin=0, vmax=1)
    plt.pause(.001)
    plt.savefig(f"logs/T{turn}_{command}_{token_list}")

    turn += 1