import trashgame

if __name__ == "__main__":
    seed, rnd_max = 347707, None    # playable ace exposes an ace on last round
    seed, rnd_max = 676079, 2       # full perfect turn
    seed -= 1   # because 1 gets added to rnd_cnt before even starting
    p1 = trashgame.Player('a')
    p2 = trashgame.Player('b')
    g = trashgame.Game(p1, p2, seed, show_output=True)
    stats = g.play(0, rnd_max)
    for s in stats:
        print(s)