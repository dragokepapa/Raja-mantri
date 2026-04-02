import random

ROLES = ["Raja", "Mantri", "Chor", "Sipahi"]

class Game:
    def __init__(self):
        self.players = []
        self.roles = {}
        self.mantri = None
        self.chor = None

    def add_player(self, user_id):
        if user_id not in self.players:
            self.players.append(user_id)

    def is_full(self, max_players):
        return len(self.players) >= max_players

    def assign_roles(self):
        roles = ROLES.copy()
        random.shuffle(roles)

        self.roles = dict(zip(self.players, roles))

        for user, role in self.roles.items():
            if role == "Mantri":
                self.mantri = user
            elif role == "Chor":
                self.chor = user

    def check_guess(self, user_id):
        return user_id == self.chor