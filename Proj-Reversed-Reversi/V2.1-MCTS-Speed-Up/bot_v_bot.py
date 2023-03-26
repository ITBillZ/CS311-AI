from game import GameState, BLACK, WHITE
from utils import print_board
import time, sys, os
from mcts import MCTSAgent

dir = os.path.abspath(os.path.dirname(__file__))
f1 = open(dir + "\\mcts_v_mcts.txt", "a")
f1.truncate(0)


f2 = open(dir + "\\result.txt", "a")
f2.truncate(0)



def main():
    sys.stdout = f1
    game = GameState.new_game()
    bots = {
        BLACK: MCTSAgent(True, use_dfs=False, temperature=6),
        WHITE: MCTSAgent(True, use_dfs=True, temperature=6),
    }

    while not game.is_over():

        start = time.perf_counter()
        bot_move = bots[game.next_player].select_move(game)
        end = time.perf_counter()
        print("Time: ", end - start)

        print(game.next_player, bot_move)

        game = game.apply_move(bot_move)
        print_board(game.board)
        print("-------------------------")
        f1.flush()
    
    sys.stdout = f2
    print("Winner", game.winner)
    f2.flush()

if __name__ == '__main__':
    for i in range(10):
        main()
    f1.close()
    f2.close()



