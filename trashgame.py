import random
import time
import datetime


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
        self.perfect_turn = 0
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

    def play(self, round, show_output):
        # decide between top discard or draw pile
        # play as long as you can
        # discard

        facedown_cnt_beg = self.faceup.count(False)
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
            if show_output:
                print("take discard",Deck.card(card))
        else:
            card = round.top_card()
            if show_output:
                print("draw top card",Deck.card(card))
        rank = Deck.rank(card)
        win = False
        # we have a card from either the discard or draw pile
        # anything higher than a JACK came from the draw pile
        # and is an automatic discard
        if rank > 10:
            if show_output:
                print('discarding drawn card', Deck.card(card))
            round.discard_card(card)
            return False
        while True:
            if play_cnt > self.streak:
                self.streak = play_cnt
                self.streak_marker = str(round.rnd_cnt) + '-' + str(round.turn_cnt)
                #q = input('new streak ' + str(play_cnt)+ " "+ self.streak_marker)
            if self.open_spot() == -1 and self.jack_location is None:
                if show_output:
                    print(self.desc, "Wins Round")
                    # discard revealed card just to keep things clean
                    print('final discard of', Deck.card(card))
                round.discard_card(card)
                win = True
                break
            if show_output:
                print("attempting to play", Deck.card(card))
            newcard = None
            if rank == 10:  # JACK
                # where to put it?
                first_open = self.open_spot()
                if first_open is None:
                    if show_output:
                        print("already have a JACK")
                else:
                    if show_output:
                        print("placing JACK at", first_open + 1)
                    self.jack_location = first_open
                    newcard = self.hand[first_open]
                    self.hand[first_open] = card
                    # DON'T set self.faceup location for JACKS
                    play_cnt += 1
                    if show_output:
                        print("revealed", Deck.card(newcard))
            else:
                if rank < self.cnt and not self.faceup[rank]:
                    if show_output:
                        print("we can use it!")
                    newcard = self.hand[rank]
                    self.hand[rank] = card
                    self.faceup[rank] = True
                    play_cnt += 1
                    if rank == self.jack_location:
                        if show_output:
                            print("trying to replay JACK")
                        self.jack_location = None
                    else:
                        if show_output:
                            print("revealed", Deck.card(newcard))
                else:
                    if show_output:
                        print("can't use it")
            if newcard:
                if show_output:
                    print('continuing')
                card = newcard
                rank = Deck.rank(card)
                newcard = None
            else:
                if show_output:
                    print('discarding', Deck.card(card))
                round.discard_card(card)
                break
        if facedown_cnt_beg == self.cnt and self.faceup.count(False) == 0:
            # started hand with everything facedown and
            # ended hand with everything face up
            self.perfect_turn = self.cnt

        return win # True or False

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

    def turn(self,player, show_output):
        if show_output:
            print("Start Turn: %s" % str(self.turn_cnt+1), repr(player))
        win = player.play(self, show_output)
        if show_output:
            print("End Turn:", repr(player))
            if player.perfect_turn:
                print("Perfect Turn!")
            print("Player end:", repr(self))
            print()
        return win

    def play(self, show_output):
        self.deal()
        winner = None
        while True:
            if show_output:
                print(self)
            p = self.players[self.start_idx % 2]
            win = self.turn(p, show_output)
            if win:
                winner = p
                break
            self.start_idx += 1  # next player
            self.turn_cnt += 0.5
            p = self.players[self.start_idx % 2]
            win = self.turn(p, show_output)
            if win:
                winner = p
                break
            self.start_idx += 1  # first player again for next turn
            self.turn_cnt += 0.5
        if winner is self.p1:
            loser = self.p2
        else:
            loser = self.p1
        return winner, loser

class Game(object):
    def __init__(self, p1, p2, random_seed, show_output=True):
        self.p1 = p1
        self.p2 = p2
        self.random_seed = random_seed
        self.show_output = show_output

    def play(self, game_nbr, rnd_max=None):
        p1 = self.p1
        p2 = self.p2
        starting_player_idx = 0
        rnd_cnt = 0
        if self.show_output:
            print('Starting Game seed=',self.random_seed)
        stats = []
        while True:
            rnd_cnt += 1
            if rnd_max is not None and rnd_cnt > rnd_max:
                if self.show_output:
                    print("stopping game for debugging")
                break
            rnd_type = "I"  # interim
            rnd = Round(p1, p2, starting_player_idx, rnd_cnt, self.random_seed + rnd_cnt)
            winner, loser = rnd.play(self.show_output)
            winner.win_round()
            loser.lose_round()
            if self.show_output:
                print("- - - - - - - - - - - - - - - ")
                print(winner.desc, "wins round!", p1.desc,"=",p1.cnt, "|", p2.desc,"=",p2.cnt)
                print("- - - - - - - - - - - - - - - ")
                print()
            if winner.victory():
                rnd_type = "F" # final
                if self.show_output:
                    print("- - - - - - - - - - - - - - - ")
                    print(winner.desc, "wins game!", p1.desc,"=",p1.cnt, "|", p2.desc,"=",p2.cnt)
                    print("- - - - - - - - - - - - - - - ")
            else:
                if winner is p1:
                    starting_player_idx = 1
                else:
                    starting_player_idx = 0

            stats.append((game_nbr,rnd_cnt,rnd_type,p1.cnt,p2.cnt,abs(p1.cnt-p2.cnt),p1.streak,p2.streak, p1.perfect_turn, p2.perfect_turn, self.random_seed, self.random_seed+rnd_cnt))
            if rnd_type == "F":
                break
        if self.show_output:
            print(p1.desc, "longest streak", p1.streak, p1.streak_marker)
            print(p2.desc, "longest streak", p2.streak, p2.streak_marker)

        return stats



