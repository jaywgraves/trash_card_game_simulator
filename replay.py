import trashgame

if __name__ == "__main__":
    # seed needs to be game seed and play through the right number of rounds
    # you can't take the rnd_seed and play from there because you need the entire
    # history of the game to be repeatable

    #seed, rnd_max = 347707, None     # playable ace exposes an ace on last round
    #seed, rnd_max = 676078, 1       # full perfect turn
    #seed, rnd_max = 504985, 17      # perfect turn on non-Final round
    seed, rnd_max = 352596, 10       # 'headshot' perfect turn of 10 on round 10 FTW

    p1 = trashgame.Player('a')
    p2 = trashgame.Player('b')
    g = trashgame.Game(p1, p2, seed, show_output=True)
    stats = g.play(0, rnd_max)
    for s in stats:
        print(s)