from AI import MapTools
from Board import Board
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def plot_fig(fig, game: Board):
    game.update_map()
    fig.clear()
    ax1 = fig.add_subplot(221)
    ax1.pcolor(np.flipud(game.sonar_enemy.map_pred), cmap=plt.cm.Greens, vmin=0, vmax=1)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax2.pcolor(np.flipud(MapTools.gen_map_from_locs(game.cannot_enter)), cmap=plt.cm.Reds, vmin=0, vmax=1)
    ax3.pcolor(np.flipud(MapTools.gen_map_from_locs(game.can_move)), cmap=plt.cm.Blues, vmin=0, vmax=1)
    ax2.pcolor(np.flipud(game.map_ally), cmap=grey_alpha, vmin=0, vmax=1)
    plt.pause(.001)
    plt.savefig(f"logs/T{game.turn}_{command}_{token_list}")

cmap = plt.cm.Greys
grey_alpha = cmap(np.arange(cmap.N))
grey_alpha[:,-1] = np.linspace(0, 1, cmap.N)
grey_alpha = ListedColormap(grey_alpha)

SHIPS = 4
MAP_SIZE = 5
POS_Y = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}

# Initialize
fig = plt.figure()
game = Board(MAP_SIZE, SHIPS)
print(game.map_ally)

if input("IS FIRST? (Y/N): ") == "Y": game.turn += 1
while(True):
    if game.turn % 2 == 0:
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
                game.atacked(atk_position)
            case "MOV":
                mov_info = (token_list[0], int(token_list[1]))
                game.moved(mov_info)
            case "EXIT":
                exit()
            case x:
                print(f"ERROR: NOT COMMAND")
                continue
    else:
        command = ""
        token_list = []
        movable = 0
        for s in game.submarines:
            movable += len(s.can_move)
        if movable == 0:
            for pos in game.sonar_enemy.index_pred:
                if pos in game.can_atack:
                    command = "ATK"
                    token_list = list(MapTools.yx2loc(pos))
                    break
        else:
            if game.hit_count != 0:
                # ATK
                if True:
                    for pos in game.sonar_enemy.index_pred:
                        if game.sonar_enemy.map_pred[pos[0]][pos[1]] == 1 and pos in game.can_atack:
                            command = "ATK"
                            token_list = list(MapTools.yx2loc(pos))
                            break
                if command != "ATK":
                    command = "MOV"
                    token_list = game.move_for_escape()
            else:
                # ATK
                command = "ATK"
                prob_atackable = 0
                for loc in game.sonar_enemy.index_pred:
                    if loc in game.can_atack:
                        prob_atackable = max(prob_atackable, game.sonar_enemy.map_pred[loc[0]][loc[1]])
                if prob_atackable != 0:
                    for loc in game.sonar_enemy.index_pred:
                        if loc in game.can_atack:
                            loc_atk = MapTools.yx2loc(loc)
                            token_list = list(loc_atk)
                            break
                        else:
                            if game.sonar_enemy.map_pred[loc[0]][loc[1]] > 0.5:
                                command = "MOV"
                                token_list = game.move_for_atack(loc)
                                break
                else:
                    loc = game.sonar_enemy.index_pred[0]
                    command = "MOV"
                    token_list = game.move_for_atack(loc)

        print(f"{command} {token_list[0]} {token_list[1]}")

        if command == "ATK":
            pos_atk = (POS_Y.get(token_list[0]), int(token_list[1]) - 1)
            print(pos_atk)
            confirm = False
            while not confirm:
                result = input("Result? : ").split()[0]
                confirm = game.atack(pos_atk, result)

    plot_fig(fig, game)
    game.turn += 1