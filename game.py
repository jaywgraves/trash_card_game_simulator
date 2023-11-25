import random
import time


class Deck(object):
    ranks = tuple('A 2 3 4 5 6 7 8 9 T J Q K'.split(' '))
    suits =  tuple('♠︎ ♥︎ ♣︎ ♦︎'.split(' '))
    colors = ('black', 'red')

    def __init__(self, shuffle=True, random_seed=None):
        # no jokers
        self.cards = list(range(52))
        if shuffle:
            if random_seed:
                random.Random(random_seed).shuffle(self.cards)
            else:
                random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def card(i):
        return Deck.ranks[Deck.rank(i)]+Deck.suits[Deck.suit(i)]

    def rank(i):
        return i % 13

    def suit(i):
        if i < 13:
            return 0
        else:
            return i // 13

    def color(i):
        return Deck.colors[Deck.suit(i) % 2]

    def cut(self,x=26):
        return self.cards[:x],self.cards[x:]

    def top_card(self):
        return self.cards.pop(0)


class Player(object):
    def __init__(self, desc):
        self.desc = desc
        self.cnt = 10
        self.streak = 0
        self.streak_marker = ""
        self.reset()

    def reset(self):
        self.jack_location = None
        self.play_cnt = 0
        self.hand = []    # these are considered face-down
        self.faceup = []

    def __repr__(self):
        rank_desc = "A 2 3 4 5 6 7 8 9 T".split()
        hand = []
        for i in range(self.cnt):
            if i == self.jack_location:
                hand.append("J")
            elif self.faceup[i]:
                hand.append(rank_desc[i])
            else:
                hand.append("_")
        return "Player {} Score {} Hand {}".format(self.desc, self.cnt, " ".join(hand))

    def deal_ready(self):
        return len(self.hand) < self.cnt

    def deal_accept(self, card):
        self.hand.append(card)
        self.faceup.append(False)

    def open_spot(self):
        if self.jack_location is not None:
            # we already have a JACK
            return None
        for i,x in enumerate(self.faceup):
            if not x:
                return i
        # no open spots, we have probably won
        return -1

    def play(self, round):
        # decide between top discard or draw pile
        # play as long as you can
        # discard
        play_cnt = 0
        card = None
        discard = round.look_discard()
        if discard:
            rank = Deck.rank(discard)
            if rank == 10:  # JACK
                if self.jack_location is None:
                    card = round.take_discard()
            if not card:
                if rank < self.cnt and not self.faceup[rank]:
                    # we want the top discard
                    card = round.take_discard()
        if card:
            print("take discard",Deck.card(card))
        else:
            card = round.top_card()
            print("draw top card",Deck.card(card))
        rank = Deck.rank(card)
        win = False
        # we have a card from either the discard or draw pile
        # anything higher than a JACK came from the draw pile
        # and is an automatic discard
        if rank > 10:
            print('discarding drawn card', Deck.card(card))
            round.discard_card(card)
            return False
        while True:
            if play_cnt > self.streak:
                self.streak = play_cnt
                self.streak_marker = str(round.rnd_cnt) + '-' + str(round.turn_cnt)
                #q = input('new streak ' + str(play_cnt)+ " "+ self.streak_marker)
            if self.open_spot() == -1 and self.jack_location is None:
                print(self.desc, "Wins Round")
                # discard revealed card just to keep things clean
                print('final discard of', Deck.card(card))
                round.discard_card(card)
                win = True
                break
            print("attempting to play", Deck.card(card))
            newcard = None
            if rank == 10:  # JACK
                # where to put it?
                first_open = self.open_spot()
                if first_open is None:
                    print("already have a JACK")
                else:
                    print("placing JACK at", first_open + 1)
                    self.jack_location = first_open
                    newcard = self.hand[first_open]
                    self.hand[first_open] = card
                    # DON'T set self.faceup location for JACKS
                    play_cnt += 1
                    print("revealed", Deck.card(newcard))
            else:
                if rank < self.cnt and not self.faceup[rank]:
                    print("we can use it!")
                    newcard = self.hand[rank]
                    self.hand[rank] = card
                    self.faceup[rank] = True
                    play_cnt += 1
                    if rank == self.jack_location:
                        print("trying to replay JACK")
                        self.jack_location = None
                    else:
                        print("revealed", Deck.card(newcard))
                else:
                    print("can't use it")
            if newcard:
                print('continuing')
                card = newcard
                rank = Deck.rank(card)
                newcard = None
            else:
                print('discarding', Deck.card(card))
                round.discard_card(card)
                break
        return win  # True or False

    def win_round(self):
        self.cnt -= 1
        self.reset()

    def lose_round(self):
        self.reset()

    def victory(self):
        return self.cnt == 0


class Round(object):
    def __init__(self, p1, p2, starting_player_idx, rnd_cnt, random_seed):
        self.p1 = p1
        self.p2 = p2
        self.deck = Deck(random_seed=random_seed)
        self.discard = []
        self.turn_cnt = 0.0
        self.rnd_cnt = rnd_cnt

        self.start_idx = starting_player_idx
        self.players = [p1, p2]

    def deal(self):
        p1full = p2full = False
        while not(p1full) or not(p2full):
            if self.p1.deal_ready():
                card = self.deck.top_card()
                self.p1.deal_accept(card)
            else:
                p1full = True
            if self.p2.deal_ready():
                card = self.deck.top_card()
                self.p2.deal_accept(card)
            else:
                p2full = True

    def look_discard(self):
        if self.discard:
            return self.discard[-1]
        else:
            return None

    def take_discard(self):
        card = self.discard.pop()
        return card

    def discard_card(self, card):
        self.discard.append(card)

    def top_card(self):
        return self.deck.cards.pop(0)

    def __repr__(self):
        top_discard = "empty"
        if self.discard:
            top_discard = Deck.card(self.look_discard())
        return "Round {} Turn {} Top Discard {}".format(self.rnd_cnt, self.turn_cnt+1, top_discard)

    def turn(self,player):
        print("Start Turn: %s" % str(self.turn_cnt+1), repr(player))
        win = player.play(self)
        print("End Turn:", repr(player))
        print("Player end:", repr(self))
        print()
        return win

    def play(self):
        self.deal()
        winner = None
        while True:
            print(self)
            p = self.players[self.start_idx % 2]
            win = self.turn(p)
            if win:
                winner = p
                break
            self.start_idx += 1  # next player
            self.turn_cnt += 0.5
            p = self.players[self.start_idx % 2]
            win = self.turn(p)
            if win:
                winner = p
                break
            self.start_idx += 1  # first player again for next turn
            self.turn_cnt += 0.5
        if winner is p1:
            loser = p2
        else:
            loser = p1
        return winner, loser

class Game(object):
    def __init__(self, p1, p2, random_seed):
        self.p1 = p1
        self.p2 = p2
        self.random_seed = random_seed
        self.rounds = []

    def play(self, game_nbr):
        starting_player_idx = 0
        rnd_cnt = 0
        print('Starting Game seed=',self.random_seed)
        stats = []
        while True:
            rnd_cnt += 1
            rnd = Round(p1, p2, starting_player_idx, rnd_cnt, self.random_seed + rnd_cnt)
            self.rounds.append(rnd)
            winner, loser = rnd.play()
            winner.win_round()
            loser.lose_round()
            print("- - - - - - - - - - - - - - - ")
            print(winner.desc, "wins round!", p1.desc,"=",p1.cnt, "|", p2.desc,"=",p2.cnt)
            print("- - - - - - - - - - - - - - - ")
            print()
            if winner.victory():
                print("- - - - - - - - - - - - - - - ")
                print(winner.desc, "wins game!", p1.desc,"=",p1.cnt, "|", p2.desc,"=",p2.cnt)
                print("- - - - - - - - - - - - - - - ")
                break
            if winner is p1:
                starting_player_idx = 1
            else:
                starting_player_idx = 0

            stats.append((game_nbr,i,p1.cnt,p2.cnt,abs(p1.cnt-p2.cnt),p1.streak,p2.streak,self.random_seed+rnd_cnt))
        print(p1.desc, "longest streak", p1.streak, p1.streak_marker)
        print(p2.desc, "longest streak", p2.streak, p2.streak_marker)

        return stats


if __name__ == '__main__':
    all_stats = []
    total_runs = 1000
    checkpoint = 100
    start = time.time()
    for i in range(total_runs):
        p1 = Player('a')
        p2 = Player('b')
        seed = random.randint(1, 1000000)
        #seed = 169338
        g = Game(p1,p2, seed)
        stats = g.play(i)
        all_stats.extend(stats)
        if (i+1) % checkpoint == 0:
            filename = format(i+1, "08d") + '_stats.csv'
            with open("data/" + filename,'w') as f:
                for s in all_stats:
                    f.write(",".join(str(x) for x in s) + "\n")
            all_stats.clear()
    end = time.time()

    print("elapsed seconds", end-start)

