import time
import datetime
import random
import os
import trashgame

if __name__ == '__main__':
    all_stats = []
    total_runs = 500
    checkpoint = 100
    show_output = True
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if os.listdir(data_dir):
        print(data_dir, "not empty.  aborting")
        raise SystemExit
    start = time.time()
    for i in range(total_runs):
        game_nbr = i+1
        p1 = trashgame.Player('a')
        p2 = trashgame.Player('b')
        seed = random.randint(1, 1000000)
        g = trashgame.Game(p1, p2, seed, show_output=show_output)
        stats = g.play(game_nbr)
        all_stats.extend(stats)
        if (game_nbr) % checkpoint == 0:
            filename = format(i+1, "08d") + '_stats.csv'
            print("saving checkpoint", filename, datetime.datetime.isoformat(datetime.datetime.now()))
            with open(os.path.join(data_dir, filename),'w') as f:
                for s in all_stats:
                    f.write(",".join(str(x) for x in s) + "\n")
            all_stats.clear()
    end = time.time()

    print("elapsed seconds", end-start)
