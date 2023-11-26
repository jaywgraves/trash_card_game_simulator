import trashgame

if __name__ == "__main__":
    seed = 676079
    seed -= 1   # because 1 gets added to rnd_cnt before even starting
    rnd_max = None
    rnd_max = 1
    p1 = trashgame.Player('a')
    p2 = trashgame.Player('b')
    g = trashgame.Game(p1, p2, seed, show_output=True)
    stats = g.play(0, rnd_max)