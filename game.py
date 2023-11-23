import itertools as it
import random


class Deck(object):
    ranks = tuple('A 2 3 4 5 6 7 8 9 T J Q K'.split(' '))
    suits =  tuple('♠︎ ♥︎ ♣︎ ♦︎'.split(' '))
    colors = ('black', 'red')

    def __init__(self, shuffle=True):
        # no jokers
        self.cards = list(range(52))
        if shuffle:
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
        self.reset()

    def reset(self):
        self.jack_location = None
        self.hand = []    # these are considered face-down
        self.faceup = []

    def __repr__(self):
        return "Player {} {} {}".format(self.desc, self.cnt, self.faceup)

    def deal_ready(self):
        return len(self.hand) < self.cnt

    def deal_accept(self, card):
        self.hand.append(card)
        self.faceup.append(False)

    def open_spot(self):
        for i,x in enumerate(self.faceup):
            if not x:
                return i
        return None

    def play(self, round):
        # decide between top discard or draw pile
        # play as long as you can
        # discard
        print(self)
        card = None
        discard = round.look_discard()
        if discard:
            rank = Deck.rank(discard)
            if rank == 10:  # JACK
                if self.jack_location is None:
                    card = round.take_discard()
            if not card:
                if rank <= self.cnt and not self.faceup[rank]:
                    # we want the top discard
                    card = round.take_discard()
        if not card:
            card = round.top_card()
        rank = Deck.rank(card)
        win = False
        # we have a card from either the discard or draw pile
        # anything higher than a JACK came from the draw pile
        # and is an automatic discard
        if rank > 10:
            round.discard_card(card)
            return False
        while True:
            if self.open_spot() is None and self.jack_location is None:
                win = True
                break
            newcard = None
            if rank == 10:  # JACK
                # where to put it?
                # this needs to check for None
                first_open = self.open_spot()
                self.jack_location = first_open
                newcard = self.hand[first_open]
                self.faceup[first_open] = True
            else:
                if rank <= self.cnt and not self.faceup[rank]:
                    # we can use it
                    newcard = self.hand[rank]
                    self.faceup[rank] = True
            if newcard:
                card = newcard
                rank = Deck.rank(card)
                newcard = None
            else:
                round.discard_card(card)
                # turn off has_jack ?
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
    def __init__(self, p1, p2, starting_player_idx):
        self.p1 = p1
        self.p2 = p2
        self.deck = Deck()
        self.discard = []
        self.turn_cnt = 0
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
        card = self.discard.pop(0)
        return card

    def discard_card(self, card):
        self.discard.append(card)

    def top_card(self):
        return self.deck.cards.pop(0)

    def play(self):
        self.deal()
        winner = None
        while True:
            p = self.players[self.start_idx % 2]
            self.turn_cnt += 0.5
            win = p.play(self)
            if win:
                winner = p
                break
            self.start_idx += 1  # next player
            p = self.players[self.start_idx % 2]
            self.turn_cnt += 0.5
            win = p.play(self)
            if win:
                winner = p
                break
            self.start_idx += 1  # first player again for next turn
            print("turn", self.turn_cnt, "discard", len(self.discard), "deck", len(self.deck))
        if winner is p1:
            loser = p2
        else:
            loser = p1
        return winner, loser

class Game(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.rounds = []

    def play(self):
        starting_player_idx = 0
        while True:
            rnd = Round(p1, p2, starting_player_idx)
            self.rounds.append(rnd)
            winner, loser = rnd.play()
            winner.win_round()
            loser.lose_round()
            if winner.victory():
                break
            if winner is p1:
                starting_player = p2
            else:
                starting_player = p1

        return {"stats":"belong here"}


if __name__ == '__main__':
    p1 = Player('a')
    p2 = Player('b')
    g = Game(p1,p2)
    stats = g.play()

