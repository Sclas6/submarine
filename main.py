from Sonar import Sonar
from Submarine import Submarine
from AI import AI, MapTools
import numpy as np
import matplotlib.pyplot as plt
import copy
from random import choice

def gen_heatmap(pred_enemy, color):
    return plt.pcolor(np.flipud(pred_enemy), cmap=color, vmin=0, vmax=1)

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
                if internal not in MapTools.get_pos(map) and mov_info[1] not in MapTools.get_pos(map):
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

# Initialize
submarines = [Submarine(loc) for loc in AI.place_submarines()]
for sub in submarines:
    print(MapTools.yx2loc(sub.location))
map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
gen_can_move(submarines, map_allies)

fig = plt.figure()

print(MapTools.gen_map_from_locs([sub.location for sub in submarines]))

# TODO 敵がいそうなところへ移動する
# TODO 移動先をかんがえる

tmp = input("IS FIRST? (Y/N): ")
if tmp == "Y": turn += 1
while(True):
    if turn % 2 == 0:
        is_atacked = False
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
                            is_atacked = True
                            sub.hit()
                            hp_allies -= 1
                            print(f"HP: {sub.hp}")
                            print(f"HP: {hp_allies}")
                            if sub.hp == 0:
                                print("\tSINK")
                                sonner_allies.detect_sink(atk_position)
                                is_atacked = False
                                for i, s in enumerate(submarines):
                                    if atk_position == s.location:
                                        del submarines[i]
                                map_allies = MapTools.gen_map_from_locs([sub.location for sub in submarines])
                            else:
                                print("\tHIT")
                                sonner_allies.detect_hit(atk_position)
                            breaked = True
                            break
                    if not breaked:
                        if atk_position in MapTools.can_atack(map_allies):
                            print("\tOBS")
                            sonner_allies.detect_obs(atk_position)
                        else:
                            sonner_allies.detect_miss(atk_position)
                            print("\tMISS")
                case "MOV":
                    sonner_enemy.detect_mov(token_list[0], int(token_list[1]))
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
        loc_atk = None
        if is_atacked:
            # ATK
            if hp_allies >= hp_enemy:
                for pos in sonner_enemy.index_pred:
                    if sonner_enemy.map_pred[pos[0]][pos[1]] == 1 and pos in MapTools.can_atack(map_allies):
                        command = "ATK"
                        loc_atk = MapTools.yx2loc(pos)
                        token_list = list(loc_atk)
                        #print(f"{command} {loc_atk[0]} {loc_atk[1]}")
                        break
            if command != "ATK":
                #print(map_alies)
                command = "MOV"
                m = 1
                ls = set()
                for sub in submarines:
                    for mov in sub.can_move:
                        print("*", end="", flush=True)
                        tmp = copy.deepcopy(sonner_allies)
                        #print(mov[0][0], mov[0][1])
                        tmp.detect_mov(mov[0][0], mov[0][1])
                        m = min(m, np.max(tmp.map_pred))
                        ls.add((np.max(tmp.map_pred), sub.location, mov))
                print("")

                ls = {n for n in ls if n[0] == m}
                n = choice(tuple(ls))
                token_list = list(n[2][0])
                #print(f"MOV {n[2][0][0]} {n[2][0][1]}")
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
                                    mov_info = choice(tuple(sub.can_move))
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
            sonner_allies.detect_obs((POS_Y.get(loc_atk[0]), int(loc_atk[1]) - 1))
            result = input("Result? : ").split()[0]
            match result:
                case "SINK":
                    hp_enemy -= 1
                    hit_position = (POS_Y.get(loc_atk[0]), int(loc_atk[1]) - 1)
                    sonner_enemy.detect_sink(hit_position)
                case "HIT":
                    hp_enemy -= 1
                    hit_position = (POS_Y.get(loc_atk[0]), int(loc_atk[1]) - 1)
                    sonner_enemy.detect_hit(hit_position)
                case "OBS":
                    obs_position = (POS_Y.get(loc_atk[0]), int(loc_atk[1]) - 1)
                    sonner_enemy.detect_obs(obs_position)
                case "MISS":
                    obs_position = (POS_Y.get(loc_atk[0]), int(loc_atk[1]) - 1)
                    sonner_enemy.detect_miss(obs_position)
    '''print(sonner_enemy.map_pred)
    print(sonner_enemy.index_pred)
    print(sonner_allies.map_pred)
    print(sonner_allies.index_pred)
    print(map_allies)'''
    fig.clear()
    ax1 = fig.add_subplot(1, 2, 1)
    ax1 = gen_heatmap(sonner_enemy.map_pred, plt.cm.Reds)
    ax2 = fig.add_subplot(1, 2, 2)
    ax2 = gen_heatmap(map_allies, plt.cm.Greys)
    plt.pause(.001)

    turn += 1