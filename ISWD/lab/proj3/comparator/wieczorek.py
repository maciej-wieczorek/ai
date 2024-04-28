import numpy as np
from player import Player

class Wieczorek(Player):
    
    def putCard(self, declared_card):
        ### check if must draw
        if len(self.cards) == 1 and declared_card is not None and self.cards[0][0] < declared_card[0]:
            return "draw"

        card = min(self.cards, key=lambda x: x[0])
        declaration = (card[0], card[1])
        if declared_card is not None:
            min_val = declared_card[0]
            if card[0] < min_val:
                valid_cards = sorted(filter(lambda x: x[0]>=min_val, self.cards))
                p = len(valid_cards) / len(self.cards)
                if len(valid_cards) > 0 and np.random.choice([True, False], p=[p, 1-p]):
                    # decided not to cheat
                    card = (valid_cards[0][0], valid_cards[0][1])
                    declaration = (card[0], card[1])
                else:
                    # decided to cheat
                    declaration = (min(min_val + 1, 14), declaration[1])

        return card, declaration
    
    def checkCard(self, opponent_declaration):
        if opponent_declaration in self.cards:
            return True
        probas = [0, 0.1, 0.3, 0.5, 0.7, 0.9]
        p = probas[opponent_declaration[0]-9]
        return np.random.choice([True, False], p=[p, 1-p])
